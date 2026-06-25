import asyncio
import os
from tabulate import tabulate
from pprint import pprint
import json
from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.context import RequestContext
from mcp.shared.metadata_utils import get_display_name
from mcp.client.stdio import stdio_client


# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",  # Using uv to run the server
    args=["run", "server", "mcp_server", "stdio"],  # We're already in snippets dir
    env={"UV_INDEX": os.environ.get("UV_INDEX", "")},
)
## ------- Tool, Resource and Prompts usage and Sampling Callback defining Code goes here -----------

async def display_tools(session: ClientSession):
    """Display available tools with human-readable names"""
    tools_response = await session.list_tools()
    for tool in tools_response.tools:
        # get_display_name() returns the title if available, otherwise the name
        display_name = get_display_name(tool)
        print(f"Tool: {display_name}")
        if tool.description:
            print(f"   {tool.description}")

async def display_resources(session: ClientSession):
    """Display available resources with human-readable names"""
    resources_response = await session.list_resources()
    for resource in resources_response.resources:
        display_name = get_display_name(resource)
        print(f"Resource: {display_name} ({resource.uri})")
    templates_response = await session.list_resource_templates()
    for template in templates_response.resourceTemplates:
        display_name = get_display_name(template)
        print(f"Resource Template: {display_name}")

async def display_prompts(session: ClientSession):
    """Display available prompts with human-readable names"""
    prompts_response = await session.list_prompts()
    for prompt in prompts_response.prompts:
        display_name = get_display_name(prompt)
        print(f"Prompt: {display_name}")
        if prompt.description:
            print(f"   {prompt.description}")


async def handle_sampling_message(
    context: RequestContext[ClientSession, None], params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    print(f"Sampling request: {params.messages}")
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="qwen3-32b",
        stopReason="endTurn",
    )

# Connecting to STDIO server
    async with stdio_client(server_params) as (read, write):
        sync with ClientSession(read, write, sampling_callback=handle_sampling_message) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            #tools = await session.list_tools()
            #print(f"Available tools: {[t.name for t in tools.tools]}")
            print("=== Available Tools ===")
            await display_tools(session)
            print("-------------------------------\n")
            # List available resources
            #resources = await session.list_resources()
            #print(f"Available resources: {[r.uri for r in resources.resources]}")
            print("\n=== Available Resources ===")
            await display_resources(session)
            print("-------------------------------\n")
            # List available prompts
            #prompts = await session.list_prompts()
            #print(f"Available prompts: {[p.name for p in prompts.prompts]}")
            print("\n=== Available Prompts ===")
            await display_prompts(session)
            print("-------------------------------\n") 
           
            # Get a prompt (generate_code_request prompt from mcp_server)
           
            prompts = await session.list_prompts()
            if prompts.prompts:
                prompt = await session.get_prompt("generate_code_request", 
                									arguments={
                												"language": "java", 
                												"task_description": "socket programming"
                												}
                								  )
                print(f"Prompt result: for \'generate_code_request\' prompt \n {prompt.messages[0].content.text}")
            print("-------------------------------\n")
            
def main():
    """Entry point for the client script."""
    asyncio.run(run())
if __name__ == "__main__":
    main()
