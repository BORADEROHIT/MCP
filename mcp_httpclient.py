import asyncio
import os
from tabulate import tabulate
from pprint import pprint
import json
from pydantic import AnyUrl
from mcp import ClientSession, types
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.context import RequestContext
from mcp.shared.metadata_utils import get_display_name
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
async def run():
	# Connecting to Streamable-HTTP server
    async with streamablehttp_client("http://localhost:8007/mcpserver") as (
        read,
        write,
        _,
    ):
        ## ------- Implementation Code -----------
def main():
    """Entry point for the client script."""
    asyncio.run(run())
if __name__ == "__main__":
    main()
