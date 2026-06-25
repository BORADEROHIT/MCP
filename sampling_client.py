import asyncio
#from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
#from langchain_cohere import ChatCohere
from langchain_ollama.chat_models import ChatOllama
from mcp_use import MCPAgent, MCPClient
from mcp.client.session import ClientSession
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ErrorData,
    TextContent
)
import os
import warnings
from rich.pretty import pprint
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
"""
# Acessing Locally Hosted Models through Ollama
def llmOllama():
    return ChatOllama(
        model = "qwen2.5:1.5b",
        temperature = 1.0,
        num_predict = 1024,
    )


## -------- Sampling Request Handler: Sampling Callback Code goes here--------------------------

async def sampling_callback(
        context: ClientSession,
        params: CreateMessageRequestParams
) -> CreateMessageResult | ErrorData:
    """
    Sampling callback implementation.
    This function receives a prompt and returns an LLM response.
    """
    # Integrate with your LLM of choice (OpenAI, Anthropic, etc.)
    prompt = params.messages[-1].content.text
    cprint(f"[green_yellow]Received Sampling Request from Server: [green_yellow][bright_yellow]{prompt}[/bright_yellow]")
    hints = params.modelPreferences.hints
    reqmodels = []
    for h in hints:
        reqmodels.append(h.name)
    cprint(f"[cyan]Requested Models:[/cyan] [bright_cyan]{reqmodels}[/bright_cyan]")
    # Other Model Preferences: (Can be used to further customize the implementation)
    cprint(f"[red1]Cost Priority:[/red1] [bright_red]{params.modelPreferences.costPriority}[/bright_red]")
    cprint(f"[green1]Speed Priority:[/green1] [bright_green]{params.modelPreferences.speedPriority}[/bright_green]")
    cprint(f"[deep_sky_blue1]Intelligence Priority:[/deep_sky_blue1] [turquoise2]{params.modelPreferences.intelligencePriority}[/turquoise2]")
    print()
    model_used = "Default"
    if "qwen" in reqmodels:
        llm2 = llmOllama()
        model_used = "Qwen2.5:1.5b"
        cprint("[bright_green]Using Qwen Model as suggested by MCP Server[/bright_green]")
        response = llm2.invoke(prompt).content
    else:
        cprint("[bright_red]Using Default Model, as none of the MCP Server suggested models are Available![/bright_red]")
        response = llmAWS().invoke(prompt).content
    cprint(f"[bright_yellow]LLM Response: [bold]{response}[/bold][/bright_yellow]")
    print()
    return CreateMessageResult(
        content=TextContent(text=response.split('\n')[-1], type="text"),
        model=model_used,
        role="assistant"
    )

async def run():
    # Loading the MCP Server;.
    config_file = "configs/sampling_server.json"  
    
    # Initialize client with Sampling support
    client = MCPClient.from_config_file(config_file, sampling_callback=sampling_callback)
    # Create MCP agent
    agent = MCPAgent(
            llm=llmAWS(),
            client=client,
            max_steps=15,
            additional_instructions = "You are a helpful assistant. response with tool output",
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
        print(f'Server: {server_name} Available Tools:\n')
        tools = await session.list_tools()
        print('='*30)
        for t in tools:
            print('Tool Name:',t.name, ' Tool Title:',t.title)
            print('Tool Descriptions:',t.description)
            print('Tool Input Schema:')
            pprint(t.inputSchema)
            print('Tool Output Schema:')
            pprint(t.outputSchema)
            print('-'*20)
        print('='*30)
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
                    cprint(f"[green_yellow]{response}[green_yellow]")
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
