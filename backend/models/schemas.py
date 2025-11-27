from typing import List
from pydantic import BaseModel, Field

from agents import Message


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    messages: List[Message] = Field(
        ...,
        examples=[[
            {
                "role": "user",
                "content": "What is a SQL injection attack?"
            },
            {
                "role": "assistant",
                "content": "A SQL injection attack is a code injection technique where an attacker inserts malicious SQL statements into an application's database query. This allows attackers to view, modify, or delete data they shouldn't have access to. For example, if a login form doesn't properly validate input, an attacker could input `' OR '1'='1` to bypass authentication."
            },
            {
                "role": "user",
                "content": "How can I prevent it in my Python Flask application?"
            }
        ]]
    )
    model: str = Field(default="gpt-4o-mini", examples=["gpt-4o-mini"])
    temperature: float = Field(default=0.7, examples=[0.7])
    max_tokens: int = Field(default=2000, examples=[2000])


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: Message
    usage: dict = Field(default_factory=dict)
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata about the response (agent type, tools used, etc.)"
    )
