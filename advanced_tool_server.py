from mcp.server.fastmcp import FastMCP
from typing import Annotated
import pandas as pd
import numpy as np
from pathlib import Path
# For Recent releases of MCP Python SDK use:
# from mcp.server.mcpserver import MCPServer
# Create an MCP server
## - Use 'MCPServer(...)' instead of FastMCP(...) for recent MCP-Python-SDK versions
# Create an MCP server
mcp = FastMCP("advanced_tool_server",  
              port=8002, 
              stateless_http=False, 
              streamable_http_path="/advtoolserver", 
              host="127.0.0.1", 
              warn_on_duplicate_tools=True)
# Adding tools
#=========================================================================================
# Helper Function
def fetch_users(dataframe, city=None, gender=None):
    """
    Fetches users from the DataFrame based on city, gender, or both.
    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        city (str, optional): The city to filter by. Defaults to None.
        gender (str, optional): The gender to filter by. Defaults to None.
    Returns:
        pd.DataFrame: A DataFrame containing the filtered users.
    """
    query_conditions = pd.Series([True] * len(dataframe)) # Start with all True
    if city:
        if city.lower()!="any" and city.lower()!="all":
            query_conditions = query_conditions & (dataframe['City'].str.lower() == city.lower())
    if gender:
        if gender.lower()!="any" and gender.lower()!="all":
            query_conditions = query_conditions & (dataframe['Gender'].str.lower() == gender.lower())
    return dataframe[query_conditions].to_dict(orient='records')
@mcp.tool(
            name = "search_user",
            title = "search user",
            annotations={
                            'readOnlyHint': True,
                            'destructiveHint': False,
                            'idempotentHint': True,
                            'openWorldHint': False
                        })
async def search_user(gender: Annotated[str, "gender of user"] | None,
                        city: Annotated[str, "city of user"] | None) -> list[dict]:
    """Search user by gender or city or both. Both gender and city are optional arguments.
    Args:
        city (str, optional): The city to filter by. Defaults to None.
        gender (str, optional): The gender to filter by. Defaults to None.
    Returns:
        result: A List of Dictionary items containing the filtered users details.
    """
    
    # Get the directory of the current script
    server_dir = Path(__file__).parent.resolve()
    df = pd.read_csv(f"{server_dir}/csvs/users.csv")
    query_conditions = pd.Series([True] * len(df)) # Start with all True
    if gender and city:
        result = fetch_users(df, gender=gender, city=city)
    elif gender:
        result = fetch_users(df, gender=gender)
    elif city:
        result = fetch_users(df, city=city)
    else:
        result = fetch_users(df)
    return result
@mcp.tool(
            name = "calculate_average",
            title = "calculate average",
            annotations={
                            'readOnlyHint': True,
                            'destructiveHint': False,
                            'idempotentHint': False,
                            'openWorldHint': False
                        })
async def calculate_average(data: Annotated[list[int] | list[float], "list of numbers"]) -> float:
    """
    Calculates the arithmetic mean of a provided list of numerical values.
    This tool is designed to process datasets such as ages or salaries to find 
    their average. It utilizes NumPy for efficient numerical computation.
    Args:
        data (list[int] | list[float]): A list containing integers or floating-point 
            numbers to be averaged. Must not be empty for a non-zero result.
    Returns:
        float: The calculated average of the input numbers. Returns 0.0 if the 
            input list is empty.
    """
    result = 0.0
    if data:
        arr= np.array(data)
        result = np.mean(arr)
    return result
#====================================================================================================
def main():
    """Entry point for the direct execution server."""
    mcp.run(transport="streamable-http")
if __name__ == "__main__":
    main()
    
