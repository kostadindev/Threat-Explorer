from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import sys

from models import ChatRequest, SuggestionRequest, SuggestionResponse, QueryRequest, QueryResponse, TableInfoResponse
from config import config
from agents import LLMAgent, ReACTAgent, MultiAgent
from db.database import db

router = APIRouter()

def get_agent_by_type(agent_type: str):
    """
    Get an agent instance by type.

    Args:
        agent_type: Type of agent ("llm", "react", or "multi")

    Returns:
        Agent instance

    Raises:
        ValueError: If agent type is unknown
    """
    agents = {
        "llm": LLMAgent,
        "react": ReACTAgent,
        "multi": MultiAgent,
    }

    if agent_type not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agents[agent_type](
        api_key=config.OPENAI_API_KEY,
        model=config.MODEL
    )


# Root endpoint moved to /api/info to avoid conflict with frontend
@router.get("/api/info")
async def api_info():
    """
    API information endpoint.

    Returns:
        dict: Welcome message and model information
    """
    return {
        "message": "Welcome to Threat Explorer API",
        "model": config.MODEL,
        "available_agents": ["llm", "react", "multi"]
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {"status": "healthy"}


@router.get("/ping")
async def ping():
    """
    Ping endpoint for server wake-up.

    Returns:
        dict: Pong response
    """
    return {"message": "pong"}


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint that routes to the specified agent (LLM, ReACT, or Multi-Agent).
    Returns a streaming response for better UX.

    - **LLM Agent**: Direct language model responses
    - **ReACT Agent**: Reasoning and acting with tool use
    - **Multi-Agent**: Multiple specialized agents coordinating

    Args:
        request: ChatRequest with history, agent_type, and configuration

    Returns:
        StreamingResponse: Agent's response streamed as text chunks

    Raises:
        HTTPException: If API key is not configured or processing fails
    """
    try:
        # Log incoming request
        print("", flush=True)
        print("=" * 80, flush=True)
        print("📨 INCOMING CHAT REQUEST", flush=True)
        print("=" * 80, flush=True)
        print(f"🤖 Agent Type: {request.agent_type}", flush=True)
        print(f"🌡️  Temperature: {request.temperature}", flush=True)
        print(f"📏 Max Tokens: {request.max_tokens}", flush=True)
        print(f"💬 Conversation History ({len(request.history)} messages):", flush=True)

        for idx, msg in enumerate(request.history, 1):
            print(f"\n   Message {idx} [{msg.role}]:", flush=True)
            content_preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            print(f"   {content_preview}", flush=True)

        print("\n" + "=" * 80, flush=True)
        print("", flush=True)

        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )

        # Get the agent instance based on request
        agent = get_agent_by_type(request.agent_type)

        # Use the agent's streaming method if available
        if hasattr(agent, 'chat_stream'):
            print(f"🔄 Using streaming response for {request.agent_type} agent", flush=True)
            print(f"📊 Visualizations: {'enabled' if request.enable_visualizations else 'disabled'}", flush=True)
            print("", flush=True)

            return StreamingResponse(
                agent.chat_stream(
                    messages=request.history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    enable_visualizations=request.enable_visualizations
                ),
                media_type="text/plain"
            )
        else:
            # Fallback to non-streaming for agents that don't support it
            print(f"🔄 Using non-streaming response for {request.agent_type} agent", flush=True)
            print(f"📊 Visualizations: {'enabled' if request.enable_visualizations else 'disabled'}", flush=True)
            print("", flush=True)

            response = agent.chat(
                messages=request.history,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                enable_visualizations=request.enable_visualizations
            )

            # Log the response
            print("", flush=True)
            print("=" * 80, flush=True)
            print("📤 AGENT RESPONSE", flush=True)
            print("=" * 80, flush=True)
            print(f"🤖 Agent: {request.agent_type}", flush=True)
            print(f"📊 Usage: {response.usage}", flush=True)
            print(f"📋 Metadata: {response.metadata}", flush=True)
            print(f"\n💬 Response Content:", flush=True)
            content_preview = response.message.content[:500] + "..." if len(response.message.content) > 500 else response.message.content
            print(f"{content_preview}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

            async def generate_fallback():
                yield response.message.content

            return StreamingResponse(
                generate_fallback(),
                media_type="text/plain"
            )
    except ValueError as e:
        print(f"❌ ValueError: {str(e)}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Exception: {str(e)}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-followups")
async def suggest_followups(_: SuggestionRequest) -> SuggestionResponse:
    """
    Generate follow-up question suggestions based on chat history.

    Returns:
        SuggestionResponse: List of suggested follow-up questions
    """
    try:
        # For now, return some generic suggestions
        # In the future, this could use the agent to generate contextual suggestions
        suggestions = [
            "Tell me more about that",
            "Can you provide an example?",
            "What are the best practices?",
        ]

        return SuggestionResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_database(request: QueryRequest) -> QueryResponse:
    """
    Execute SQL query on the cybersecurity attacks database.

    Args:
        request: QueryRequest with SQL query and optional limit

    Returns:
        QueryResponse: Query results as list of dictionaries

    Raises:
        HTTPException: If query execution fails
    """
    try:
        print("", flush=True)
        print("=" * 80, flush=True)
        print("📨 DIRECT DATABASE QUERY REQUEST", flush=True)
        print("=" * 80, flush=True)
        print(f"📝 SQL: {request.sql}", flush=True)
        print(f"📏 Limit: {request.limit}", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)

        # Add LIMIT clause if not present in query
        sql = request.sql.strip()
        if request.limit and "LIMIT" not in sql.upper():
            sql = f"{sql} LIMIT {request.limit}"

        # Execute query
        results = db.query(sql)

        print("", flush=True)
        print("=" * 80, flush=True)
        print("📤 QUERY RESPONSE", flush=True)
        print("=" * 80, flush=True)
        print(f"✅ Returned {len(results)} rows", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)

        return QueryResponse(
            data=results,
            row_count=len(results)
        )
    except Exception as e:
        print(f"❌ Query error: {str(e)}", file=sys.stderr, flush=True)
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/db/info")
async def get_database_info() -> TableInfoResponse:
    """
    Get information about the attacks database table.

    Returns:
        TableInfoResponse: Table schema and row count
    """
    try:
        info = db.get_table_info()
        return TableInfoResponse(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
