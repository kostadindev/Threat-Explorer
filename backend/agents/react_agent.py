from typing import List
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from .base import BaseAgent, Message, AgentResponse
from constants import REACT_AGENT_SYSTEM_PROMPT
from tools import query_db_tool, get_db_info


class ReACTAgent(BaseAgent):
    """
    Tool-calling agent that can query the database.
    Uses OpenAI's native tool calling for efficient execution.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            temperature=0
        )
        self.tools = self._create_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def _create_tools(self) -> List:
        """Create tools for the agent to use"""
        return [
            query_db_tool(),
            get_db_info(),
        ]

    def chat(
        self,
        messages: List[Message],
        temperature: float = 1,
        **kwargs
    ) -> AgentResponse:
        """
        Args:
            messages: Conversation history
            temperature: Sampling temperature

        Returns:
            AgentResponse with agent's reply
        """
        # Convert our Message objects to LangChain message format
        lc_messages = [SystemMessage(content=REACT_AGENT_SYSTEM_PROMPT)]

        for msg in messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        if len(lc_messages) == 1:  # Only system message
            return AgentResponse(
                message=Message(role="assistant", content="No messages provided."),
                usage={},
                metadata={"agent_type": "react", "error": "No messages"}
            )

        try:
            print("=" * 80, flush=True)
            print("🤖 ReACT AGENT - Starting", flush=True)
            print(f"📝 Messages: {len(lc_messages) - 1}", flush=True)
            print(f"🔧 Available tools: {[tool.name for tool in self.tools]}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Call LLM with tools
                response = self.llm_with_tools.invoke(lc_messages)
                lc_messages.append(response)

                # Check if there are tool calls
                if not response.tool_calls:
                    # No more tool calls, we have the final answer
                    break

                # Execute tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    print(f"🔧 Calling tool: {tool_name}", flush=True)
                    print(f"📝 Arguments: {tool_args}", flush=True)

                    # Find and execute the tool
                    tool_result = None
                    for tool in self.tools:
                        if tool.name == tool_name:
                            # Tools created with @tool are callable directly
                            tool_result = tool.invoke(tool_args)
                            break

                    # Add tool result to messages
                    lc_messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                    )
                    print(f"✅ Tool result received", flush=True)

            print("", flush=True)
            print("=" * 80, flush=True)
            print("✅ ReACT AGENT - Complete", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

            # Get the final response content
            final_message = lc_messages[-1]
            content = final_message.content if hasattr(final_message, "content") else str(final_message)

            return AgentResponse(
                message=Message(role="assistant", content=content),
                usage={},
                metadata={
                    "agent_type": "react",
                    "tools_used": [tool.name for tool in self.tools],
                    "iterations": iteration
                }
            )

        except Exception as e:
            print(f"❌ ReACT AGENT - Error: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return AgentResponse(
                message=Message(
                    role="assistant",
                    content=f"I encountered an error while processing your request: {str(e)}"
                ),
                usage={},
                metadata={"agent_type": "react", "error": str(e)}
            )

    def chat_stream(
        self,
        messages: List[Message],
        temperature: float = 1,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Process messages with streaming support.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of the response as they arrive
        """
        # Convert our Message objects to LangChain message format
        lc_messages = [SystemMessage(content=REACT_AGENT_SYSTEM_PROMPT)]

        for msg in messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        if len(lc_messages) == 1:  # Only system message
            yield "No messages provided."
            return

        try:
            print("=" * 80, flush=True)
            print("🌊 ReACT AGENT - STREAMING MODE", flush=True)
            print(f"📝 Messages: {len(lc_messages) - 1}", flush=True)
            print(f"🔧 Available tools: {[tool.name for tool in self.tools]}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

            # Create streaming LLM
            llm = ChatOpenAI(
                model=self.model,
                openai_api_key=self.api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=True
            )
            llm_with_tools = llm.bind_tools(self.tools)

            max_iterations = 5
            iteration = 0
            final_response = None

            # Execute tool calls before streaming
            while iteration < max_iterations:
                iteration += 1

                # Non-streaming call to check for tool calls
                response = llm_with_tools.invoke(lc_messages)
                lc_messages.append(response)

                # Check if there are tool calls
                if not response.tool_calls:
                    # No more tool calls, save this as final response
                    final_response = response
                    break

                # Execute tool calls
                print("", flush=True)
                print(f"🔧 Tool calls detected (iteration {iteration})", flush=True)
                print(f"📞 Number of tool calls: {len(response.tool_calls)}", flush=True)
                print("", flush=True)

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    print(f"🔧 Calling tool: {tool_name}", flush=True)
                    print(f"📝 Arguments: {tool_args}", flush=True)

                    # Find and execute the tool
                    tool_result = None
                    for tool in self.tools:
                        if tool.name == tool_name:
                            tool_result = tool.invoke(tool_args)
                            break

                    # Add tool result to messages
                    lc_messages.append(
                        ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"]
                        )
                    )
                    print(f"✅ Tool result received", flush=True)

            print("", flush=True)
            print("✅ Tool execution complete - starting stream", flush=True)
            print("", flush=True)

            # Stream the final response
            chunk_count = 0
            if final_response and final_response.content:
                # Stream the content we already have in chunks
                content = final_response.content
                chunk_size = 30  # Stream in chunks for smooth UX
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    chunk_count += 1
                    yield chunk
            else:
                # Make a streaming API call for the final response
                for chunk in llm_with_tools.stream(lc_messages):
                    if chunk.content:
                        chunk_count += 1
                        yield chunk.content

            print("", flush=True)
            print(f"✅ Streaming complete - sent {chunk_count} chunks", flush=True)
            print("", flush=True)

        except Exception as e:
            print(f"❌ ReACT AGENT - Error: {str(e)}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            yield f"I encountered an error while processing your request: {str(e)}"

    def get_agent_type(self) -> str:
        return "react"
