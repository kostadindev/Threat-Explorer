# MCP Database Access

The Threat Explorer now includes MCP (Model Context Protocol) support for database access.

## What's Included

### 1. Database Query Tools for Agents

Both the **LLM Agent** and **ReACT Agent** can now query the cybersecurity attacks database:

- **LLM Agent**: Uses OpenAI function calling to query the database
- **ReACT Agent**: Uses LangChain tools to query the database

Available tools:
- `query_database`: Execute SQL queries on the attacks table
- `get_database_info`: Get database schema and metadata

### 2. Standalone MCP Server

An MCP server is available for external clients at `backend/mcp/database_server.py`.

## Using Database Tools with Agents

### Example Queries

Ask the agents questions like:

- "How many malware attacks are in the database?"
- "Show me the top 5 most common attack types"
- "What are the critical severity attacks from the last month?"
- "Find attacks from source IP 103.216.15.12"

### LLM Agent

The LLM agent will automatically use function calling to query the database:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {"role": "user", "content": "How many malware attacks are in the database?"}
    ],
    "agent_type": "llm"
  }'
```

### ReACT Agent

The ReACT agent has access to database tools along with search and threat analysis:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {"role": "user", "content": "Find critical attacks and analyze their patterns"}
    ],
    "agent_type": "react"
  }'
```

## Running the MCP Server (Optional)

The MCP server can be used by external MCP clients:

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Running the Server

```bash
python backend/mcp/database_server.py
```

### MCP Configuration

The MCP server is configured in `mcp_config.json`:

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["backend/mcp/database_server.py"],
      "description": "MCP server for querying the cybersecurity attacks database"
    }
  }
}
```

## Database Schema

The `attacks` table contains the following columns:

- Timestamp
- Source IP Address, Destination IP Address
- Source Port, Destination Port
- Protocol
- Packet Length, Packet Type, Traffic Type
- Payload Data
- Malware Indicators
- Anomaly Scores
- Alerts/Warnings
- Attack Type
- Attack Signature
- Action Taken
- Severity Level
- User Information, Device Information
- Network Segment
- Geo-location Data
- Proxy Information
- Firewall Logs
- IDS/IPS Alerts
- Log Source

### SQL Query Examples

```sql
-- Get attack type distribution
SELECT "Attack Type", COUNT(*) as count
FROM attacks
GROUP BY "Attack Type"

-- Find critical attacks
SELECT * FROM attacks
WHERE "Severity Level" = 'Critical'
LIMIT 10

-- Search by IP
SELECT * FROM attacks
WHERE "Source IP Address" = '103.216.15.12'

-- Count by severity
SELECT "Severity Level", COUNT(*) as count
FROM attacks
GROUP BY "Severity Level"
ORDER BY count DESC
```

**Note**: Column names with spaces must be quoted with double quotes in SQL queries.
