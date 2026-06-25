
import asyncio
#from dotenv import load_dotenv
#from langchain_cohere import ChatCohere
from mcp_use import MCPAgent, MCPClient
#from langchain_ollama.chat_models import ChatOllama
import os
import warnings
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
    config_file = "configs/resource_server.json"
    client = MCPClient.from_config_file(config_file)
    # Create MCP agent
    agent = MCPAgent(
            llm=llmAWS(),
            client=client,
            max_steps=15,
            additional_instructions = "You are a helpful assistant. response using the resource information",
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
        print(f'Server: {server_name} Available Resources:\n')
        resources = await session.list_resources()
        print('='*30)
        for r in resources:
            print('Resource URI:',r.uri, ' | Resource Name:',r.name, ' | Resource Title:',r.title)
            print('Resource Descriptions:',r.description,' | Resource MIME Type:',r.mimeType)
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
