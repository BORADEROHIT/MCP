import asyncio
#from dotenv import load_dotenv
#from langchain_cohere import ChatCohere
from mcp_use import MCPAgent, MCPClient
from langchain_aws import ChatBedrockConverse
#from langchain_ollama.chat_models import ChatOllama
import os
import warnings
from rich import print as cprint
warnings.filterwarnings("ignore", category=Warning)
os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
# Reading and setting 
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
# Acessing Locally Hosted Models through Ollama
def llmOllama():
    return ChatOllama(
        model = "llama3.2:3b",
        temperature = 1.0,
        num_predict = 1024,
    )

"""
async def run():
    # Loading the MCP Server;.
    config_file = "configs/prompt_server.json"
    client = MCPClient.from_config_file(config_file)
    # Create MCP agent
    agent = MCPAgent(
            llm=llmAWS(),
            client=client,
            max_steps=15,
            additional_instructions = "You are a helpful assistant. response using the best available prompts, resource information and tools",
            memory_enabled=True, # Enable built-in conversation memory
            #use_server_manager=True # Enable the server manager
        )
    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")
    
    server_names = client.get_server_names()
    await client.create_all_sessions()
    print(server_names)
    for server_name in server_names:
        session = client.get_session(server_name)
        prompts = await session.list_prompts()
        resources = await session.list_resources()
        tools = await session.list_tools()
        cprint('[bright_yellow]=[/bright_yellow]'*60)
        
        if prompts:
            cprint(f'Server: [bright_red]{server_name}[/bright_red] Available Prompts:\n')
            for p in prompts:
                cprint(f"Prompt Name: [bright_red]{p.name}[/bright_red] | Prompt Title: [bright_red]{p.title}[/bright_red]")
                cprint(f"Prompt Descriptions: [bright_red]\n{p.description}[/bright_red]")
                if p.arguments:
                    print('Prompt Arguments:')
                    for arg in p.arguments:
                        cprint(f"[bright_red]  - {arg.name}: {arg.description}[/bright_red]", end=" | ")
                    print()
                cprint('[cornsilk1]-[/cornsilk1]'*60)
            cprint('[bright_yellow]=[/bright_yellow]'*60)
        
        
        if resources:
            cprint(f'Server: [bright_green]{server_name}[/bright_green] Available Resources:\n')
            for r in resources:
                cprint(f"Resource URI: [bright_green]{r.uri}[/bright_green] | Resource Name: [bright_green]{r.name}[/bright_green] | Resource Title: [bright_green]{r.title}[/bright_green]")
                cprint(f"Resource Descriptions: [bright_green]{r.description}[/bright_green] | Resource MIME Type: [bright_green]{r.mimeType}[/bright_green]")
                cprint('[cornsilk1]-[/cornsilk1]'*60)
            cprint('[bright_yellow]=[/bright_yellow]'*60)
        
        if tools:
            cprint(f"Server: [bright_cyan]{server_name}[/bright_cyan] Available Tools:\n")
            for t in tools:
                cprint(f"Tool Name: [bright_cyan]{t.name}[/bright_cyan] | Tool Title: [bright_cyan]{t.title}[/bright_cyan]")
                cprint(f"Tool Descriptions: [bright_cyan]{t.description}[/bright_cyan]")
                cprint('[cornsilk1]-[/cornsilk1]'*60)
            cprint('[bright_yellow]=[/bright_yellow]'*60)
    try:
            # Main chat loop
            while True:
                # Get user input
                user_input = input("\nYou: ")
                # Check for exit command
                if user_input.lower() in ["exit", "quit", ""]:
                    print("Ending conversation...")
                    break
                # Check for clear history command
                if user_input.lower() == "clear":
                    agent.clear_conversation_history()
                    print("Conversation history cleared.")
                    continue
                # Get response from agent
                print("\nAssistant: ", end="", flush=True)
                try:
                    # Run the agent with the user input (memory handling is automatic)
                    response = await agent.run(user_input)
                    print(response)
                except Exception as e:
                    print(f"\nError: {e}")
    finally:
        # Clean up
        print("Cleaning")
        await agent.close()           
def main():
    asyncio.run(run())
if __name__ == "__main__":
    main()
