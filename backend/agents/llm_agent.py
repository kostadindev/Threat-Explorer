from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .base import BaseAgent, Message, AgentResponse
from constants import LLM_AGENT_SYSTEM_PROMPT


class LLMAgent(BaseAgent):
    """
    Simple LLM agent that directly uses the language model.
    Best for straightforward question-answering without tool use.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key
        )

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using direct LLM inference.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            AgentResponse with LLM's reply
        """
        # Extract system prompts and conversation messages separately
        system_messages = [SystemMessage(content=LLM_AGENT_SYSTEM_PROMPT)]
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                # Use custom system prompt if provided, otherwise use default
                system_messages = [SystemMessage(content=msg.content)]
            elif msg.role == "user":
                conversation_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                conversation_messages.append(AIMessage(content=msg.content))

        # Combine: system messages first, then conversation
        langchain_messages = system_messages + conversation_messages

        # Create LLM instance with parameters
        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key
        )

        # Get response
        response = llm.invoke(langchain_messages)

        # Extract usage
        usage = {}
        if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
            token_usage = response.response_metadata["token_usage"]
            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

        return AgentResponse(
            message=Message(role="assistant", content=response.content),
            usage=usage,
            metadata={"agent_type": "llm"}
        )

    def chat_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Process messages using direct LLM inference with streaming.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of the response as they arrive
        """
        # Extract system prompts and conversation messages separately
        system_messages = [SystemMessage(content=LLM_AGENT_SYSTEM_PROMPT)]
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                # Use custom system prompt if provided, otherwise use default
                system_messages = [SystemMessage(content=msg.content)]
            elif msg.role == "user":
                conversation_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                conversation_messages.append(AIMessage(content=msg.content))

        # Combine: system messages first, then conversation
        langchain_messages = system_messages + conversation_messages

        # Create LLM instance with parameters
        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key,
            streaming=True
        )

        # Stream response
        for chunk in llm.stream(langchain_messages):
            if chunk.content:
                yield chunk.content

    def get_agent_type(self) -> str:
        return "llm"
