import asyncio
#from langchain_cohere import ChatCohere
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from langchain_ollama.chat_models import ChatOllama
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langgraph.checkpoint.memory import InMemorySaver
#from dotenv import load_dotenv
from uuid import uuid4
#load_dotenv()
# Accessing remotely hosted models through API key
def llmAWS():
    return ChatBedrockConverse(
        model_id="amazon.nova-lite-v1:0", 
        temperature=0.9, 
        region_name="us-east-1")

"""
def llmCohere():
    return ChatCohere(
        id='command-a-03-2025',
        temperature=0.9
    )

""" 
# Acessing Locally Hosted Models through Ollama
def llmOllama():
    return ChatOllama(
        model = "llama3.2:3b",
        temperature = 1.0,
        num_predict = 1024,
    )
async def run_mcp_agent() -> None:
    '''LangChain Agent with MCP Server Tools'''
    print("LangChain Agent with MCP Server Tools")
    ## Configuring MCP Client using Streamable-HTTP Transport
    async with streamable_http_client("http://127.0.0.1:8002/advtoolserver") as (
        read_stream,
        write_stream,
        _,
    ):
        # Create a session using the client streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
    
            ## Connecting to MCP Server to get Tools
            tools = await load_mcp_tools(session)
            print('#'*100)
            print("\nAvailable MCP Tools:")
            for t in tools:
                print('Tool Name:',t.name)
                print('Tool Descriptions:',t.description)
                print('='*50)
            print('#'*100)
            
            # Creating Agent
            agent = create_agent(
                model=llmAWS(),
                tools=tools,
                checkpointer=InMemorySaver(),
                system_prompt="You are a helpful AI assistant. Use the provided tools to answer questions."
            )
            try:
                    # Main chat loop
                    while True:
                        # Get user input
                        user_input = input("\nYou: ")
                        # Check for exit command
                        if user_input.lower() in ["exit", "quit", ""]:
                            print("Ending conversation...")
                            break
                        # Get response from agent
                        print("\nAssistant: ", end="", flush=True)
                        try:
                            # Run the agent with the user input (memory handling is automatic)
                            response = await agent.ainvoke(
                                                            {"messages": [{"role": "user", "content": user_input}]},
                                                            config={'configurable':{'thread_id':uuid4().hex}}
                                                        )
                            print(response["messages"][-1].content)
                        except Exception as e:
                            print(f"\nError: {e}")
            finally:
                # Resource Clean up
                print("Cleaning")
                tools.clear()
async def main():
    print("-----LangChain + MCP Demo------")
    await run_mcp_agent()
if __name__ == "__main__":
    asyncio.run(main())
