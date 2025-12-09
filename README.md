# CHIA Threat Explorer

**Threat Explorer** is an advanced, AI-powered cybersecurity analysis platform designed to assist security professionals in identifying, analyzing, and mitigating threats. It combines a powerful multi-agent backend with a modern, interactive frontend to provide a seamless threat intelligence experience.

## 🚀 Key Features

*   **🤖 Multi-Agent Architecture**:
    *   **LLM Agent**: Direct interaction with Large Language Models for general queries.
    *   **ReAct Agent**: Reasoning and Acting agent capable of using tools like search and threat analysis.
    *   **Multi-Agent System**: A coordinated team of specialized agents (Threat Analyst, Defense Specialist, Compliance Expert).
*   **🛡️ Threat Analysis Tools**: Integrated tools for assessing threat severity and searching for real-time intelligence.
*   **📊 Interactive Visualization**: Dynamic charts and tables for visualizing threat data and query results.
*   **💬 Context-Aware Chat**: Multi-turn conversation capabilities with history retention.
*   **🐳 Dockerized Deployment**: Easy-to-deploy containerized application for consistent environments.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, LangChain, Pydantic
*   **Frontend**: React 19, TypeScript, Vite, Ant Design, Tailwind CSS
*   **Database**: SQLite (In-memory/CSV loaded)
*   **AI/ML**: OpenAI GPT Models

## 🏁 Quick Start

The easiest way to run Threat Explorer is using Docker.

### Prerequisites

*   Docker installed on your machine.
*   An OpenAI API Key.

### Run with Docker

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e MODEL=gpt-4o-mini \
  kostadindev/threat-explorer:latest
```

Access the application at: `http://localhost:8000`

### Run with Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  web:
    image: kostadindev/threat-explorer:latest
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL=gpt-4o-mini
```

Run:
```bash
docker-compose up
```

## 💻 Development Setup

If you want to run the backend and frontend locally for development:

### Backend

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env with your OPENAI_API_KEY
    ```
5.  Run the server:
    ```bash
    python main.py
    ```

### Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## ⚙️ Configuration

Configuration is managed via environment variables.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Your OpenAI API Key (Required) | - |
| `AGENT_TYPE` | Agent mode: `llm`, `react`, or `multi` | `llm` |
| `MODEL` | OpenAI Model ID | `gpt-4o-mini` |
| `HOST` | Server Host | `0.0.0.0` |
| `PORT` | Server Port | `8000` |
| `CORS_ORIGINS` | Allowed CORS Origins | `*` |

## 📚 Documentation

*   [Backend Documentation](backend/README.md)
*   [Frontend Documentation](frontend/README.md)
*   [Docker Instructions](DOCKER_RUN.md)
*   [Logging Guide](LOGGING.md)
*   [Deployment Guide](DEPLOY.md)

## 📄 License

This project is licensed under the MIT License.