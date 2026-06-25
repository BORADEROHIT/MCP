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
# Create an MCP server
mcp = FastMCP("sales_data_server",  
              port=8007, 
              stateless_http=False, 
              streamable_http_path="/salesdataserver", 
              host="127.0.0.1", 
              warn_on_duplicate_tools=True)
# Adding tools
@mcp.tool(
            name = "get_quarterly_sales_data",
            title = "Get Sales Data",
            annotations={
                            'readOnlyHint': True,
                            'destructiveHint': False,
                            'idempotentHint': False,
                            'openWorldHint': False
                        })
async def get_quarterly_sales_data() -> dict | str:
    """
    Retrieves and summarizes the 2025 quarterly sales records for ABC Infosystems.
    This tool reads the sales dataset from a local CSV file, performs a temporal 
    conversion on date fields to assist with time-series reasoning, and generates 
    a high-level financial summary alongside the raw data.
    Returns:
        dict | str: A dictionary containing the following keys if successful:
            - 'total_records' (int): Total number of sales entries found.
            - 'columns' (list): List of available data fields in the CSV.
            - 'total_revenue' (float): The sum of all revenue across all quarters.
            - 'top_region' (str): The geographical region with the highest total revenue.
            - 'quarterly_breakdown' (dict): Total revenue grouped by quarter (Q1-Q4).
            - 'complete_data' (list[dict]): The full dataset in record-oriented format.
            
            Returns an error message string if the file is missing or data processing fails.
    Args:
        None: This function does not accept any input arguments.
    """
    try:
        script_dir = Path(__file__).parent.resolve()
        file_path = f"{script_dir}/csvs/salesdata.csv"
        #print(file_path)
        df = pd.read_csv(file_path)
        #print(df)
        # Convert date to datetime for better agent reasoning
        df['Date'] = pd.to_datetime(df['Date'])
        
        summary = {
            "total_records": len(df),
            "columns": list(df.columns),
            "total_revenue": df['Total_Revenue'].sum(),
            "top_region": df.groupby('Region')['Total_Revenue'].sum().idxmax(),
            "quarterly_breakdown": df.groupby('Quarter')['Total_Revenue'].sum().to_dict(),
            "complete_data": df.to_dict(orient='records')
        }
        return summary
    except Exception as e:
        return f"Error reading dataset: {e}"
def main():
    """Entry point for the direct execution server."""
    mcp.run(transport="streamable-http")
if __name__ == "__main__":
    main()
