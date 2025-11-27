from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from agents import Message


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    history: List[Message] = Field(
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
    agent_type: str = Field(default="llm", examples=["llm", "react", "multi"])
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


class SuggestionRequest(BaseModel):
    """Request model for suggestion endpoint"""
    history: List[Message] = Field(
        ...,
        description="Chat history to generate suggestions from"
    )


class SuggestionResponse(BaseModel):
    """Response model for suggestion endpoint"""
    suggestions: List[str] = Field(
        default_factory=list,
        description="List of suggested follow-up questions"
    )


class QueryRequest(BaseModel):
    """Request model for database query endpoint"""
    sql: str = Field(
        ...,
        description="SQL query to execute",
        examples=["SELECT * FROM attacks LIMIT 10"]
    )
    limit: Optional[int] = Field(
        default=100,
        description="Maximum number of rows to return",
        examples=[100]
    )


class QueryResponse(BaseModel):
    """Response model for database query endpoint"""
    data: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Query results as list of dictionaries"
    )
    row_count: int = Field(
        description="Number of rows returned"
    )


class TableInfoResponse(BaseModel):
    """Response model for table info endpoint"""
    table_name: str = Field(description="Name of the table")
    columns: List[Dict[str, str]] = Field(description="List of column definitions")
    row_count: int = Field(description="Total number of rows in the table")
