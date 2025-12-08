# Comprehensive Request & Tool Call Logging

The Threat Explorer now includes comprehensive logging for all requests, responses, tool calls, and database operations. Every interaction is logged with detailed information.

## What Gets Logged

### 1. Incoming Chat Requests
Every chat request is logged with full details:
- Agent type being used
- Temperature and max tokens settings
- Complete conversation history
- Each message role and content (with preview)

Example:
```
================================================================================
📨 INCOMING CHAT REQUEST
================================================================================
🤖 Agent Type: llm
🌡️  Temperature: 0.7
📏 Max Tokens: 2000
💬 Conversation History (1 messages):

   Message 1 [user]:
   How many malware attacks are in the database?

================================================================================
```

### 2. LLM Agent Decision Making
The LLM agent logs its decision process:
- Whether it's using function calling mode or streaming mode
- Available tools
- Whether it decided to use tools or provide direct response
- Reasoning for tool selection

Example:
```
================================================================================
🤖 LLM AGENT - FUNCTION CALLING MODE
================================================================================
🔧 Available tools: ['get_database_info', 'query_database']
================================================================================

🔄 Sending initial request to LLM...
✅ LLM decided to use 1 tool(s)
```

or

```
ℹ️  LLM decided NOT to use any tools - providing direct response
```

### 3. Database Initialization
When the server starts, you'll see:
- Database connection status
- CSV loading progress
- Number of rows loaded
- Table creation

Example:
```
================================================================================
🗄️  DATABASE INITIALIZATION
================================================================================
📦 Creating in-memory SQLite database...
✅ Database connection established
📂 Loading data from: /path/to/cybersecurity_attacks.csv
📋 Found 25 columns
✅ Created 'attacks' table
   Inserted 1000 rows...
   Inserted 2000 rows...
✅ Successfully loaded 2500 rows into database
================================================================================
```

### 4. LLM Agent Tool Calls
When the LLM agent uses function calling to query the database:
- Tool call iterations
- Tool names and arguments
- Result sizes
- Total tools used

Example:
```
================================================================================
🤖 LLM AGENT - Tool Call Iteration 1
📞 Number of tool calls: 1
================================================================================

🔧 Tool Call #1
   Name: query_database
   Arguments: {
      "query": "SELECT \"Attack Type\", COUNT(*) as count FROM attacks GROUP BY \"Attack Type\""
   }
   Result length: 1234 characters

🔄 Getting LLM response with tool results...

================================================================================
✅ LLM AGENT - Tool calling complete
📊 Total tools used: ['query_database']
================================================================================
```

### 5. Database Tool Execution
Every database query shows:
- Query being executed
- Whether LIMIT was added automatically
- Number of rows returned
- Sample result (first row)
- Success/error status

Example:
```
================================================================================
🔧 TOOL CALL: query_database
📝 Query: SELECT * FROM attacks WHERE "Attack Type" = 'Malware'
⚠️  Added LIMIT 20 to query
🔍 Executing SQL: SELECT * FROM attacks WHERE "Attack Type" = 'Malware' LIMIT 20
✅ Query successful! Returned 50 rows
📊 Sample result: {'Timestamp': '2023-05-30 06:33:58', 'Attack Type': 'Malware', ...}
================================================================================
```

### 6. Agent Response Output
After processing, the response is logged:
- Agent type used
- Token usage statistics
- Metadata (tools used, etc.)
- Response content preview

Example:
```
================================================================================
📤 AGENT RESPONSE
================================================================================
🤖 Agent: llm
📊 Usage: {'prompt_tokens': 234, 'completion_tokens': 56, 'total_tokens': 290}
📋 Metadata: {'agent_type': 'llm', 'tools_used': ['query_database']}

💬 Response Content:
Based on the database query, there are 1,234 malware attacks in the database...
================================================================================
```

### 7. Streaming Mode
When using streaming responses:
- Notification that streaming mode is active
- Warning that streaming doesn't support tool calls
- Chunk count as response streams

Example:
```
================================================================================
🌊 LLM AGENT - STREAMING MODE
================================================================================
⚠️  Note: Streaming mode does not support function calling/tool use
    For database queries, use non-streaming mode (agent_type='llm')
================================================================================

🔄 Starting to stream response chunks...

✅ Streaming complete - sent 45 chunks
```

### 8. Direct Database Queries
Direct API queries to `/query` endpoint:
- SQL query being executed
- Limit parameter
- Number of rows returned

Example:
```
================================================================================
📨 DIRECT DATABASE QUERY REQUEST
================================================================================
📝 SQL: SELECT * FROM attacks WHERE "Attack Type" = 'Malware'
📏 Limit: 100
================================================================================

================================================================================
📤 QUERY RESPONSE
================================================================================
✅ Returned 50 rows
================================================================================
```

### 9. ReACT Agent Execution
The ReACT agent logs:
- Start of reasoning loop
- User query
- Available tools
- Completion status
- Detailed LangChain agent verbose output

Example:
```
================================================================================
🤖 ReACT AGENT - Starting reasoning loop
📝 User query: Find critical attacks in the database
🔧 Available tools: ['Search', 'ThreatAnalysis', 'QueryDatabase', 'GetDatabaseInfo']
================================================================================

[LangChain verbose output follows...]

================================================================================
✅ ReACT AGENT - Reasoning complete
================================================================================
```

## Complete Request Flow Example

Here's what a complete request looks like in the logs:

```
================================================================================
📨 INCOMING CHAT REQUEST
================================================================================
🤖 Agent Type: llm
🌡️  Temperature: 0.7
📏 Max Tokens: 2000
💬 Conversation History (1 messages):

   Message 1 [user]:
   How many malware attacks are in the database?

================================================================================

🔄 Using non-streaming response for llm agent

================================================================================
🤖 LLM AGENT - FUNCTION CALLING MODE
================================================================================
🔧 Available tools: ['get_database_info', 'query_database']
================================================================================

🔄 Sending initial request to LLM...
✅ LLM decided to use 1 tool(s)

================================================================================
🤖 LLM AGENT - Tool Call Iteration 1
📞 Number of tool calls: 1
================================================================================

🔧 Tool Call #1
   Name: query_database
   Arguments: {
      "query": "SELECT COUNT(*) as count FROM attacks WHERE \"Attack Type\" = 'Malware'"
   }
   Result length: 234 characters

================================================================================
🔧 TOOL CALL: query_database
📝 Query: SELECT COUNT(*) as count FROM attacks WHERE "Attack Type" = 'Malware'
⚠️  Added LIMIT 20 to query
🔍 Executing SQL: SELECT COUNT(*) as count FROM attacks WHERE "Attack Type" = 'Malware' LIMIT 20
✅ Query successful! Returned 1 rows
📊 Sample result: {'count': '1234'}
================================================================================

🔄 Getting LLM response with tool results...

================================================================================
✅ LLM AGENT - Tool calling complete
📊 Total tools used: ['query_database']
================================================================================

================================================================================
📤 AGENT RESPONSE
================================================================================
🤖 Agent: llm
📊 Usage: {'prompt_tokens': 234, 'completion_tokens': 56, 'total_tokens': 290}
📋 Metadata: {'agent_type': 'llm', 'tools_used': ['query_database']}

💬 Response Content:
Based on the database query, there are 1,234 malware attacks in the database.
================================================================================
```

## Viewing Logs

### Start the Server
```bash
cd backend
python main.py
```

You'll see logs in the console as the server starts and handles requests.

### Test with Example Script
```bash
# In a new terminal, with the server running
python test_tool_logging.py
```

This script will:
1. Query database info
2. Run a direct SQL query
3. Ask the LLM agent to query the database
4. (Optionally) Test the ReACT agent

Check the server terminal to see all the detailed logs!

### Manual Testing

#### Test LLM Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {"role": "user", "content": "How many attacks are in the database?"}
    ],
    "agent_type": "llm"
  }'
```

#### Test ReACT Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "history": [
      {"role": "user", "content": "What are the most common attack types?"}
    ],
    "agent_type": "react"
  }'
```

## Log Levels

The logging is configured with `INFO` level by default. You can adjust this in the code:

```python
# In any module with logging
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## Example Queries to Try

Ask the agents questions like:

1. **"How many malware attacks are in the database?"**
   - LLM will call `get_database_info` then `query_database`

2. **"Show me the top 5 attack types"**
   - LLM will query and format results

3. **"Find all critical severity attacks"**
   - LLM will filter by severity level

4. **"What's the distribution of attacks by protocol?"**
   - LLM will group by protocol and count

Watch the server console to see each tool call in detail!

## Log Emoji Guide

- 🚀 Server startup
- 🗄️ Database initialization
- 📨 Incoming request
- 📤 Outgoing response
- 🤖 Agent activity
- 🌊 Streaming mode
- 🔧 Tool call
- 📝 Query/input
- 🔍 Execution
- ✅ Success
- ❌ Error
- ⚠️ Warning
- ℹ️ Information
- 📊 Data/results
- 📋 Schema/metadata
- 📏 Parameters/limits
- 🌡️ Temperature setting
- 💬 Conversation/message
- 🔄 Processing
- 📞 Number of calls
