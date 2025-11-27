from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models import ChatRequest, SuggestionRequest, SuggestionResponse
from config import config
from core import get_agent

router = APIRouter()

# Initialize agent (can easily switch between LLM, ReACT, or Multi-Agent via config)
agent = get_agent()


@router.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: Welcome message, agent type, and model information
    """
    return {
        "message": "Welcome to Threat Explorer API",
        "agent_type": agent.get_agent_type(),
        "model": config.MODEL
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
    Chat endpoint that routes to the configured agent (LLM, ReACT, or Multi-Agent).
    Returns a streaming response for better UX.

    - **LLM Agent**: Direct language model responses
    - **ReACT Agent**: Reasoning and acting with tool use
    - **Multi-Agent**: Multiple specialized agents coordinating

    Args:
        request: ChatRequest with history and configuration

    Returns:
        StreamingResponse: Agent's response streamed as text chunks

    Raises:
        HTTPException: If API key is not configured or processing fails
    """
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )

        # Use the agent's streaming method if available
        if hasattr(agent, 'chat_stream'):
            return StreamingResponse(
                agent.chat_stream(
                    messages=request.history,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ),
                media_type="text/plain"
            )
        else:
            # Fallback to non-streaming for agents that don't support it
            response = agent.chat(
                messages=request.history,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )

            async def generate_fallback():
                yield response.message.content

            return StreamingResponse(
                generate_fallback(),
                media_type="text/plain"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-followups")
async def suggest_followups(request: SuggestionRequest) -> SuggestionResponse:
    """
    Generate follow-up question suggestions based on chat history.

    Args:
        request: SuggestionRequest with chat history

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
