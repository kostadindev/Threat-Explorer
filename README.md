# Threat Explorer

A cybersecurity threat analysis chatbot for exploring recorded attacks through natural language conversations.

## Overview

Threat Explorer enables security experts to analyze cybersecurity data without extensive knowledge of SQL or database schemas. It uses a Retrieval-Augmented Generation (RAG) system to convert natural language queries into SQL, retrieve attack records, and generate visual or text-based responses.

**Dataset:** Inscribo's cybersecurity dataset (40,000 records, 25 columns) including Source IP, Attack Type, Anomaly Score, Severity Levels, Protocols, and timestamps.

**Example Queries:**
- "Show the last 10 attacks with an anomaly score over 75"
- "Show the number of high severity attacks grouped by attack type"
- "What protocols are most commonly used in DDoS attacks?"

## Features

- **Three Agent Architectures:** LLM Chain (fastest, most efficient), ReAct (most reliable), Multi-Agent (experimental)
- **Conversation Management:** Save, load, and download dialogues in JSON format
- **SQL Transparency:** View and inspect generated SQL queries with syntax highlighting

## Quick Start

### Prerequisites

- Python 3.13
- Node.js 18+
- OpenAI API key

### 1. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Build frontend
npm run build
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python13 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run backend server
python main.py
```

The backend serves both the API and the built frontend at `http://localhost:8000`

## Project Structure

```
Threat-Explorer/
  backend/                    # FastAPI backend
    agents/                   # Agent implementations
      llm_chain.py            # Basic LLM chain agent
      react.py                # ReAct agent (most reliable)
      multi_agent.py          # Multi-agent orchestration
    api/                      # API routes and endpoints
    db/                       # Database layer
      database.py             # SQLite connection and schema
      cybersecurity_attacks.csv  # Source dataset
    models/                   # Pydantic schemas
    tools/                    # Agent tools (SQL execution, schema inspection)
    utils/                    # Utilities (logging, conversation storage)
    main.py                   # FastAPI application entry point
    config.py                 # Configuration loader
    constants.py              # System prompts and constants
    evaluate_agents.py        # Agent evaluation scripts
    requirements.txt          # Python dependencies

  frontend/                   # React frontend
    src/
      components/            # UI components (ChatWindow, MessageList, Header)
      services/              # API client
      types/                 # TypeScript types
      hooks/                 # React hooks
      config/                # Frontend configuration
      App.tsx                # Main React component
    package.json              # Node dependencies

  DEPLOY.md                   # Deployment guide
  DOCKER_RUN.md               # Docker instructions
  LOGGING.md                  # Logging documentation
  README.md                   # This file
```

## Configuration

Edit `backend/.env`:

```env
OPENAI_API_KEY=sk-... # Your OpenAI API key
```


## Research

This system was developed as part of a technical and design study comparing agent architectures and visualization strategies. See the full research report in the repository for:
- Agent performance benchmarks (retrieval accuracy, speed, cost)
- User study results (N=12, visualizations vs. text-only)
- Statistical analysis and design recommendations

