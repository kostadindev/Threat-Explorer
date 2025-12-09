<<<<<<< HEAD
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
=======
<img width="1704" height="883" alt="image" src="https://github.com/user-attachments/assets/7ef98644-b46c-4899-8c43-5e7b43078ace" /># Threat Explorer
>>>>>>> 9c335911977c841c24f0efff5297eaed0002dfb4

### Run with Docker

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e MODEL=gpt-4o-mini \
  kostadindev/threat-explorer:latest
```


<img width="1710" height="890" alt="image" src="https://github.com/user-attachments/assets/05dba7dd-9d14-4448-a418-d24c5b7fb7a6" />


<img width="1704" height="887" alt="image" src="https://github.com/user-attachments/assets/7c6e4506-ceb0-4154-bc1f-d41fd0fd55a5" />

<img width="1706" height="886" alt="image" src="https://github.com/user-attachments/assets/8d9a3775-bdb1-4865-a302-1b8c53dd7077" />

<img width="1704" height="883" alt="image" src="https://github.com/user-attachments/assets/b548d876-bd0a-4eba-9050-dc6611701520" />

