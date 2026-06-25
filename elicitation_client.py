import asyncio
#from langchain_cohere import ChatCohere
from rich.pretty import pprint
#from dotenv import load_dotenv
from mcp_use import MCPAgent, MCPClient
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult
from langchain_aws import ChatBedrockConverse
from langchain_ollama.chat_models import ChatOllama
import os
import warnings
warnings.filterwarnings("ignore", category=Warning)
os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
from rich import print as cprint
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
async def elicitation_callback(
    context: RequestContext,
    params: ElicitRequestParams
) -> ElicitResult:
    """
    Elicitation callback implementation.
    This function receives a request for user inputs and returns the user's response.
    Example showing how to use all parameters."""
    # Access the user message
    user_message = params.message
    cprint(f"[bright_yellow]Server Request: {user_message}[/bright_yellow]")
    #print(hasattr(params, 'requestedSchema'))
    #print(params.requestedSchema)
    # Check if schema is provided for structured data
    if hasattr(params, 'requestedSchema') and params.requestedSchema:
        schema = getattr(params, 'requestedSchema', None)
        # Handle structured input based on the requested schema
        cprint("[bright_green]Requested Schema:[/bright_green]")
        pprint(schema)
        
        print()
        schema_type = schema.get('type')
        if schema_type == 'object':
            properties = schema.get('properties', {})
            cprint(f"[green_yellow]Expecting {schema_type} with fields: {list(properties.keys())}[/green_yellow]")
            # Collect structured data for each property
            user_data = {}
            required_fields = []
            for field_name, field_def in properties.items():
                mandatory_field, field_type = 'Optional', 'Undefined'
                if 'type' in field_def.keys():
                    field_type = field_def.get('type', 'string')
                    mandatory_field= ' *(Mandatory Field)'
                    required_fields.append(field_name)
                else:
                    if 'anyOf' in field_def.keys():
                        field_type = field_def.get('anyOf')[0]['type']
                field_description = field_def.get('description', '')
                prompt = f"{field_name} ({field_type} - {field_description} - {mandatory_field}):"
                # Display the message to the user and collect their input
                value = input(prompt)
                # Perform type conversion on collected input based on field type 
                if field_type == 'string':
                    value = value.lower().strip() if value else None
                elif field_type == 'number':
                    value = float(value) if value else None
                elif field_type == 'integer':
                    value = int(value) if value else None
                elif field_type == 'boolean':
                    value = value.lower() in ('true', '1', 'yes') if value else None
                
                user_data[field_name] = value
            
            # Validate required fields
            missing_fields = [field for field in required_fields 
                                if field not in user_data or not user_data[field]]
            if missing_fields:
                cprint(f"[bright_red]]Missing required fields: {missing_fields}[/bright_red]")
                return ElicitResult(action="cancel")
            
            # Return the elicitation result
            return ElicitResult(action="accept", content=user_data)
    
async def run():
    # Loading the MCP Server;.
    config_file = "configs/elicitation_server.json"
    # Initialize client with Elicitation support
    client = MCPClient.from_config_file(config_file, 
                                        elicitation_callback=elicitation_callback)    
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
