import asyncio
from agno.agent import Agent, RunOutput
from agno.tools.mcp import MCPTools
#from agno.models.ollama import Ollama
#from agno.models.cohere import Cohere
from agno.models.aws import AwsBedrock
from rich.pretty import pprint
from rich import print as cprint
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
load_dotenv()
# Acessing Locally Hosted Models through Ollama
def llmOllama():
    return Ollama(id="qwen2.5:1.5b") # "llama3.2:3b",
# Accessing remotely hosted models through API key
def llmAWS():
    return AwsBedrock(id="amazon.nova-lite-v1:0", 
                    aws_region="us-east-1", 
                    temperature=0.9)
"""
def llmCohere():
    return Cohere(id='command-a-03-2025',
                temperature=0.9)
"""
async def run_mcp_agent() -> None:
    '''Agno Agent with MCP Server Tools'''
    print("Agno Agent with MCP Server Tools")
    # Initialize the MCP tools using Streamable-HTTP Transport
    mcp_tools_server1 = MCPTools(url="http://127.0.0.1:8001/toolserver",transport="streamable-http")
    # Connect to the MCP server
    await mcp_tools_server1.connect()
    print("Available MCP Tools:")
    print('='*100)
    tools = await mcp_tools_server1.session.list_tools()
    for t in tools.tools:
        print('Tool Name:',t.name)
        print('Tool Descriptions:',t.description)
        print('-'*50)
    print('='*100)
    # Uncomment to observe the 'call_tool' partial functions as entrypoints bound to the MCP Tools 
    # that are to be executed when the corresponding tool call is predicted by LLM of the Agent
    # In Python, functools.partial is a utility used for partial function application. 
    # It allows you to "freeze" a portion of a function's arguments or keywords, 
    # creating a new object with a simplified signature.
    # It creates a new callable that behaves like the original function but with some arguments already set.
    # print("Tools with Corresponding Call_Tool Partial Fuctions:")
    # print('='*100)
    # funcs = mcp_tools_server1.get_functions()
    # for t,f in funcs.items():
    #     print('Tool Name:',t)
    #     pprint(f)
    #     print('-'*50)
    # print('='*100)
    
    # Initialize the Agent with LLM and MCP Tools
    agent = Agent(  
                    model=llmAWS(),
                    markdown=True, 
                    tools=[mcp_tools_server1]
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
                try:
                    # Run the agent with the user input (memory handling is automatic)
                    response: RunOutput = await agent.arun(user_input)
                    cprint(f"[bright_yellow]\nFinal Agent Response:[/bright_yellow]")
                    print("\nAssistant: ", end="", flush=True)
                    cprint(f"[bright_yellow]{response.content}[/bright_yellow]")
                    print()
                except Exception as e:
                    print(f"\nError: {e}")
    finally:
        # Resource Clean up
        print("Cleaning")
        await mcp_tools_server1.close()
async def main():
    print("-----Agno + MCP Demo------")
    await run_mcp_agent()
if __name__ == "__main__":
    asyncio.run(main())
    
