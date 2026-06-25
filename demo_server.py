from mcp.server.fastmcp import FastMCP
# Create an MCP server
mcp = FastMCP(name = "Demo_server",
		   instructions="""
        	   This server provides data analysis tools.
        	   Call hello() to get a greeting message.
    	   """)
@mcp.tool()
async def hello(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"
def main():
    """Entry point for the direct execution server."""
    mcp.run(transport="stdio")
if __name__ == "__main__":
    main()
