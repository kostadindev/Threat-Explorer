"""MCP Server for Database Access"""
import asyncio
import json
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

from db.database import db


# Create MCP server instance
app = Server("database-server")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available database tools"""
    return [
        types.Tool(
            name="query_database",
            description="""Query the cybersecurity attacks database using SQL.

The database contains a table called 'attacks' with cybersecurity attack data including:
- Timestamp: When the attack occurred
- Source IP Address, Destination IP Address
- Source Port, Destination Port
- Protocol: Network protocol used
- Attack Type: Type of attack (e.g., Malware, DDoS, Intrusion)
- Severity Level: Severity of the attack (Low, Medium, High, Critical)
- Malware Indicators, Anomaly Scores
- Action Taken, Alerts/Warnings
- Geo-location Data, Network Segment
- And many more fields

Input should be a valid SQL query string. The query will be automatically limited to 50 rows if no LIMIT is specified.

Example queries:
- SELECT * FROM attacks WHERE "Attack Type" = 'Malware' LIMIT 5
- SELECT "Attack Type", COUNT(*) as count FROM attacks GROUP BY "Attack Type"
- SELECT * FROM attacks WHERE "Severity Level" = 'Critical' LIMIT 10

Note: Column names with spaces must be quoted with double quotes.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute on the attacks table"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_database_info",
            description="""Get information about the cybersecurity attacks database schema.

Returns the table name, total number of rows, and all available columns with their types.
Use this to understand what data is available before querying.""",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle tool execution requests"""

    if name == "query_database":
        try:
            query = arguments.get("query", "")

            # Add LIMIT if not present
            sql = query.strip()
            if "LIMIT" not in sql.upper():
                sql = f"{sql} LIMIT 50"

            results = db.query(sql)

            if not results:
                response = {
                    "success": True,
                    "row_count": 0,
                    "message": "Query executed successfully but returned no results.",
                    "data": []
                }
            else:
                response = {
                    "success": True,
                    "row_count": len(results),
                    "data": results
                }

            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]

        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e),
                "message": "Failed to execute query. Check your SQL syntax."
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]

    elif name == "get_database_info":
        try:
            info = db.get_table_info()

            # Format column information
            columns_formatted = "\n".join([
                f"  - {col['name']} ({col['type']})"
                for col in info['columns']
            ])

            response = {
                "success": True,
                "table_name": info["table_name"],
                "total_rows": info["row_count"],
                "columns": info["columns"],
                "description": f"Database contains {info['row_count']} cybersecurity attack records with the following columns:\n{columns_formatted}"
            }

            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]

        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e)
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server"""
    # Initialize database
    db.initialize()
    print("Database initialized for MCP server", flush=True)

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="database-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
