from fastapi import APIRouter, HTTPException

from models import ChatRequest, ChatResponse
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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint that routes to the configured agent (LLM, ReACT, or Multi-Agent).

    - **LLM Agent**: Direct language model responses
    - **ReACT Agent**: Reasoning and acting with tool use
    - **Multi-Agent**: Multiple specialized agents coordinating

    Args:
        request: ChatRequest with messages and configuration

    Returns:
        ChatResponse: Agent's response with message, usage, and metadata

    Raises:
        HTTPException: If API key is not configured or processing fails
    """
    try:
        if not config.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )

        # Use the agent to generate response
        response = agent.chat(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            message=response.message,
            usage=response.usage,
            metadata=response.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
