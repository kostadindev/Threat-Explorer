"""Database query tools for agents"""
import json
import sys

from db.database import db


def query_database(query: str) -> str:
    """
    Execute a SQL query on the cybersecurity attacks database.

    Args:
        query: SQL query string to execute

    Returns:
        JSON string with query results or error message
    """
    print("=" * 80, flush=True)
    print("🔧 TOOL CALL: query_database", flush=True)
    print(f"📝 Query: {query}", flush=True)

    try:
        # Limit results to prevent overwhelming the context
        sql = query.strip()
        if "LIMIT" not in sql.upper():
            sql = f"{sql} LIMIT 50"
            print(f"⚠️  Added LIMIT 50 to query", flush=True)

        print(f"🔍 Executing SQL: {sql}", flush=True)
        results = db.query(sql)
        print(f"✅ Query successful! Returned {len(results)} rows", flush=True)

        if not results:
            print("ℹ️  No results returned", flush=True)
            print("=" * 80, flush=True)
            return json.dumps({
                "success": True,
                "row_count": 0,
                "message": "Query executed successfully but returned no results.",
                "data": []
            })

        print(f"📊 Sample result: {results[0] if results else 'None'}", flush=True)
        print("=" * 80, flush=True)
        return json.dumps({
            "success": True,
            "query": sql,  # Include the executed query
            "row_count": len(results),
            "data": results
        }, indent=2)

    except Exception as e:
        print(f"❌ Query failed: {str(e)}", file=sys.stderr, flush=True)
        print("=" * 80, flush=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to execute query. Check your SQL syntax."
        })


def get_database_info() -> str:
    """
    Get information about the cybersecurity attacks database schema.

    Returns:
        JSON string with database schema information
    """
    print("=" * 80, flush=True)
    print("🔧 TOOL CALL: get_database_info", flush=True)

    try:
        info = db.get_table_info()

        print(f"📋 Table: {info['table_name']}", flush=True)
        print(f"📊 Total rows: {info['row_count']}", flush=True)
        print(f"📑 Columns: {len(info['columns'])}", flush=True)

        # Format column information nicely
        columns_formatted = "\n".join([
            f"  - {col['name']} ({col['type']})"
            for col in info['columns']
        ])

        print("✅ Database info retrieved successfully", flush=True)
        print("=" * 80, flush=True)

        return json.dumps({
            "success": True,
            "table_name": info["table_name"],
            "total_rows": info["row_count"],
            "columns": info["columns"],
            "description": f"Database contains {info['row_count']} cybersecurity attack records with the following columns:\n{columns_formatted}"
        }, indent=2)

    except Exception as e:
        print(f"❌ Failed to get database info: {str(e)}", file=sys.stderr, flush=True)
        print("=" * 80, flush=True)
        return json.dumps({
            "success": False,
            "error": str(e)
        })


def query_db_tool():
    """
    Create a LangChain Tool for database queries.

    Returns:
        Tool instance configured for database queries
    """
    from langchain_core.tools import tool

    @tool
    def QueryDatabase(query: str) -> str:
        """Query the cybersecurity attacks database using SQL.

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

        Use this tool to query attack patterns, statistics, and specific attack details.
        The query will be automatically limited to 50 rows if no LIMIT is specified.

        Example queries:
        - SELECT * FROM attacks WHERE "Attack Type" = 'Malware' LIMIT 5
        - SELECT "Attack Type", COUNT(*) as count FROM attacks GROUP BY "Attack Type"
        - SELECT * FROM attacks WHERE "Severity Level" = 'Critical' LIMIT 10

        Note: Column names with spaces must be quoted with double quotes.

        Args:
            query: SQL query string to execute on the attacks table

        Returns:
            JSON string with query results or error message
        """
        return query_database(query)

    return QueryDatabase


def get_db_info():
    """
    Create a LangChain Tool for getting database schema information.

    Returns:
        Tool instance configured for database info
    """
    from langchain_core.tools import tool

    @tool
    def GetDatabaseInfo() -> str:
        """Get information about the cybersecurity attacks database schema.

        Use this tool to understand what data is available in the database before querying it.
        It returns the table name, total number of rows, and all available columns with their types.
        This tool does not require any input.

        Returns:
            JSON string with database schema information
        """
        return get_database_info()

    return GetDatabaseInfo
