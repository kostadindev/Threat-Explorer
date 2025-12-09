# Threat Explorer Backend

FastAPI backend with multi-agent cybersecurity assistant.

## Project Structure

```
backend/
├── agents/              # Agent system
│   ├── __init__.py
│   ├── base.py         # Base agent class and models
│   ├── llm_agent.py    # Simple LLM agent
│   ├── react_agent.py  # ReAct agent with tools
│   └── multi_agent.py  # Multi-agent coordinator
├── api/                 # API routes
│   ├── __init__.py
│   └── routes.py       # Route handlers
├── core/                # Core utilities
│   ├── __init__.py
│   └── agent_factory.py # Agent factory function
├── models/              # Pydantic models
│   ├── __init__.py
│   └── schemas.py      # Request/response schemas
├── main.py             # FastAPI app initialization
├── config.py           # Application configuration
├── constants.py        # System prompts and constants
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in git)
└── .env.example        # Example environment configuration
```

## Features

- **🤖 Three Agent Types**: LLM, ReAct, and Multi-Agent
- **🔧 Tool Use**: ReAct agent can use search and threat analysis tools
- **👥 Specialized Agents**: Multi-agent system with threat analysis, defense, and compliance specialists
- **💬 Multi-turn Conversations**: Maintains conversation history
- **🔒 Type-safe**: Uses Pydantic models for validation
- **🌐 CORS Support**: Configurable CORS for frontend integration
- **📚 Auto-generated API Docs**: Available at `/docs` and `/redoc`

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
python main.py
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /chat` - Chat with LLM (supports conversation history)

Visit `http://localhost:8000/docs` for interactive API documentation.

## Agent Types

### 1. LLM Agent (`AGENT_TYPE=llm`)
Simple, direct language model responses. Best for straightforward Q&A.

**Use case**: General cybersecurity questions, definitions, explanations

### 2. ReAct Agent (`AGENT_TYPE=react`)
Reasoning and Acting agent with tool access. Uses a thought-action-observation loop.

**Available tools**:
- **Search**: DuckDuckGo search for current threat intelligence
- **ThreatAnalysis**: Severity assessment of security threats

**Use case**: Questions requiring current information or threat analysis

### 3. Multi-Agent (`AGENT_TYPE=multi`)
Coordinates multiple specialized agents for comprehensive answers.

**Specialists**:
- **Threat Analysis Specialist**: Attack vectors, vulnerabilities, malware
- **Defense & Mitigation Specialist**: Security best practices, incident response
- **Compliance & Policy Expert**: GDPR, HIPAA, frameworks, audits
- **General Security Advisor**: Broad cybersecurity topics

**Use case**: Complex questions requiring multiple perspectives

## Switching Agents

Change the `AGENT_TYPE` in `.env`:

```bash
# Simple LLM responses
AGENT_TYPE=llm

# ReAct with tools
AGENT_TYPE=react

# Multi-agent coordination
AGENT_TYPE=multi
```

Restart the server to apply changes.

## Configuration

All configuration is managed through environment variables in `.env`:

- `AGENT_TYPE` - Which agent to use: `llm`, `react`, or `multi` (default: "llm")
- `OPENAI_API_KEY` - OpenAI API key
- `MODEL` - OpenAI model to use (default: "gpt-4o-mini")
- `HOST` - Server host (default: "0.0.0.0")
- `PORT` - Server port (default: 8000)
- `CORS_ORIGINS` - Allowed CORS origins (default: "*")

## Examples

### Using LLM Agent
```bash
# .env
AGENT_TYPE=llm

# Test query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is phishing?"}
    ]
  }'
```

### Using ReAct Agent
```bash
# .env
AGENT_TYPE=react

# Test query (will use search tool)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the latest ransomware trends in 2024?"}
    ]
  }'
```

### Using Multi-Agent
```bash
# .env
AGENT_TYPE=multi

# Test query (routes to defense specialist)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "How can I secure my web application against XSS attacks?"}
    ]
  }'
```
