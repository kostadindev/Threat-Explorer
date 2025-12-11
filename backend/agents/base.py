from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Message model for chat interactions"""
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["What is a SQL injection attack?"])
    timestamp: Optional[str] = Field(default=None, examples=["2025-12-09T10:30:00.000Z"])
    agent_type: Optional[str] = Field(default=None, description="Type of agent that generated this message (for assistant messages)", examples=["llm", "react", "multi"])


class AgentResponse(BaseModel):
    """Standard response format for all agents"""
    message: Message
    usage: Dict[str, int] = Field(default_factory=dict)
    metadata: Optional[Dict] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agent types"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process chat messages and return a response.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional agent-specific parameters

        Returns:
            AgentResponse with the agent's reply
        """
        pass

    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the type of agent (llm, react, multi)"""
        pass
