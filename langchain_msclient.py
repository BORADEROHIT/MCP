import asyncio
import json
#from langchain_cohere import ChatCohere
from rich.pretty import pprint
from rich import print as cprint
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_aws import ChatBedrockConverse
from langchain_ollama.chat_models import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult
from langchain.messages import ToolMessage
from uuid import uuid4
#from dotenv import load_dotenv
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

# Helper Function to Read Server Configurations from JSON File
def read_json_as_dict(filename: str)->dict:
    """
    Reads a JSON file and returns its content as a Python dictionary.
    """
    try:
        with open(filename, 'r') as file:
            # Use json.load() to deserialize the file content into a Python object
            data_dict = json.load(file)
            return data_dict
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file '{filename}'. Check file formatting.")
        return None
# Elicitation Request Handler: Code for Elicitation Callback goes here----------------------
async def on_elicitation(
    mcp_context: RequestContext,
    params: ElicitRequestParams,
    context: CallbackContext,
) -> ElicitResult:
    """
    Handle elicitation requests from MCP servers.
    This function receives a request for user inputs and returns the user's response.
    """
    # Access the user message
    user_message = params.message
    cprint(f"[bright_yellow]Server Request: {user_message}[/bright_yellow]")
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
async def run_mcp_agent() -> None:
    '''LangChain Agent with MCP Server Tools'''
    print("LangChain Agent with MCP Server Tools")
    ##---------MCP Client and Agent Implementation Code goes here-----------------
    ## Configuring Multi-Server MCP Client with Multiple MCP Servers
    config_file = "configs/mcpservers.json"
    configs = dict(read_json_as_dict(config_file))
    pprint(configs)
    client = MultiServerMCPClient(configs,
                                  callbacks=Callbacks(on_elicitation=on_elicitation))
    ## Tools from Multiple MCP Servers
    tools = await client.get_tools()   
    print('#'*100)
    print("\nTools:")
    for t in tools:
        print('Tool Name:',t.name)
        print('Tool Descriptions:',t.description)
        print('='*50)
    print('#'*100)
	# Uncomment to observe the 'call_tool' coroutines bound to the MCP Tools 
    # that are to be executed when the corresponding tool call is predicted by LLM of the Agent
    # In Python, a 'coroutine' object is an instance returned when you call a function defined with 
    # the async def keyword. Unlike regular functions, calling an asynchronous function does not 
    # execute its body immediately; instead, it creates a "lazy" object that represents a task to be 
    # performed later.
    # print("Tools with Corresponding Call_Tool Fuctions:")
    # pprint(tools)
    # Initialize Agent with System Prompt, LLM, Memory, and Tools
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
                
                try:
                    cprint(f"[bright_yellow]\nIntermediate Event Updates from Agent:[/bright_yellow]")
                    # Run the agent with the user input (memory handling is automatic)
                    async for event in agent.astream({"messages": [{"role": "user", "content": user_input}]}, 
                                              stream_mode="values", 
                                              config={'configurable':{'thread_id':uuid4().hex}}):
                        event["messages"][-1].pretty_print()
                    
                    # Printing Final Response from the Agent
                    print('================================================================================')
                    cprint(f"[bright_yellow]\nFinal Agent Response:[/bright_yellow]")
                    print("\nAssistant: ", end="", flush=True)
                    cprint(f"[bright_yellow]{event["messages"][-1].content}[/bright_yellow]")
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
