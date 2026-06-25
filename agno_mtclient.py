import asyncio
from agno.agent import Agent, RunOutput
from agno.tools.mcp import MultiMCPTools
#from agno.models.ollama import Ollama
#from agno.models.cohere import Cohere
from agno.models.aws import AwsBedrock
import warnings
warnings.filterwarnings("ignore")
from rich import print as cprint
from dotenv import load_dotenv
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
    print("Agno Agent with Multi-MCP Server Tools")
    # Initialize the MultiMCP tools
    multi_mcp_tools = MultiMCPTools(
        commands=["uv run server/demo_server.py"],
        urls = ["http://127.0.0.1:8001/toolserver",
                "http://127.0.0.1:8002/advtoolserver"],
        urls_transports = ['streamable-http','streamable-http']
    )
    
    # Connect to the Multiple MCP servers
    await multi_mcp_tools.connect()
    print("Available MCP Tools:")
    print('='*100)
    tools = multi_mcp_tools.get_functions()
    for t,f in tools.items():
        print('Tool Name:',t)
        # Uncomment to observe the 'call_tool' partial functions as entrypoints bound to the MCP Tools
        # print("Corresponding Call_Tool Partial Fuction:")
        # pprint(f)
        print('-'*50)
    print('='*100)
    # Initialize the Agent
    agent = Agent(  model=llmAWS(),
                    markdown=True, 
                    tools=[multi_mcp_tools]
                )
    # Run the agent
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
        # Close the MCP connection
        print("Cleaning")
        await multi_mcp_tools.close()
async def main():
    print("-----Agno + MCP Demo------")
    await run_mcp_agent()
if __name__ == "__main__":
    asyncio.run(main())
    
