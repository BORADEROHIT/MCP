from mcp.server.fastmcp import FastMCP
# For Recent releases of MCP Python SDK use:
# from mcp.server.mcpserver import MCPServer
# Create an MCP server
## - Use 'MCPServer(...)' instead of FastMCP(...) for recent MCP-Python-SDK versions
# Create an MCP server
mcp = FastMCP("Demo_http_server",  
              port=8000, 
              stateless_http=False, 
              streamable_http_path="/my_mcp", 
              host="127.0.0.1")
@mcp.tool()
async def hello(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}! I am a demo HTTP Transport MCP Server!"
@mcp.tool()
async def add(a : int, b : int)->int:
    """
    Performs addition of two numbers.
    Arguments:
        a (int): The first variable of the addition operation
        b (int): the second variable of the addition operation
    Returns:
        sum (int): The sum of the two numbers
    """
    sum = a + b
    return sum
    
def main():
    """Entry point for the direct execution server."""
    mcp.run(
            transport="streamable-http", 
            )
if __name__ == "__main__":
    main()
