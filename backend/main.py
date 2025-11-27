import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Threat Explorer API")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)


class Message(BaseModel):
    role: str = Field(..., examples=["user"])
    content: str = Field(..., examples=["What is a SQL injection attack and how can I prevent it?"])


class ChatRequest(BaseModel):
    messages: List[Message] = Field(
        ...,
        examples=[[
            {
                "role": "system",
                "content": "You are a cybersecurity expert assistant. Provide clear, accurate information about security threats and best practices."
            },
            {
                "role": "user",
                "content": "What is a SQL injection attack and how can I prevent it?"
            }
        ]]
    )
    model: str = Field(default="gpt-4o-mini", examples=["gpt-4o-mini"])
    temperature: float = Field(default=0.7, examples=[0.7])
    max_tokens: int = Field(default=2000, examples=[2000])


class ChatResponse(BaseModel):
    message: Message
    usage: dict

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Threat Explorer API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured"
            )

        # Convert request messages to LangChain message types
        langchain_messages = []
        for msg in request.messages:
            if msg.role == "system":
                langchain_messages.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))

        # Update LLM parameters for this request
        llm_instance = ChatOpenAI(
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Invoke the LLM
        response = llm_instance.invoke(langchain_messages)

        # Extract token usage if available
        usage = {}
        if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
            token_usage = response.response_metadata["token_usage"]
            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

        return ChatResponse(
            message=Message(
                role="assistant",
                content=response.content
            ),
            usage=usage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
