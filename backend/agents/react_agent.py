from typing import List
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from .base import BaseAgent, Message, AgentResponse
from constants import REACT_AGENT_SYSTEM_PROMPT, get_system_prompt
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
        enable_visualizations: bool = True,
        **kwargs
    ) -> AgentResponse:
        """
        Args:
            messages: Conversation history
            temperature: Sampling temperature
            enable_visualizations: Whether to enable database visualizations

        Returns:
            AgentResponse with agent's reply
        """
        # Convert our Message objects to LangChain message format
        system_prompt = get_system_prompt(REACT_AGENT_SYSTEM_PROMPT, enable_visualizations)
        lc_messages = [SystemMessage(content=system_prompt)]

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
            print(f"📊 Visualizations: {'enabled' if enable_visualizations else 'disabled'}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

            max_iterations = 5
            iteration = 0

            # Track token usage across all iterations
            total_input_tokens = 0
            total_output_tokens = 0
            sql_queries_executed = []

            while iteration < max_iterations:
                iteration += 1

                # Call LLM with tools
                response = self.llm_with_tools.invoke(lc_messages)
                lc_messages.append(response)

                # Track token usage if available
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    total_input_tokens += response.usage_metadata.get('input_tokens', 0)
                    total_output_tokens += response.usage_metadata.get('output_tokens', 0)
                elif hasattr(response, 'response_metadata'):
                    usage = response.response_metadata.get('token_usage', {})
                    total_input_tokens += usage.get('prompt_tokens', 0)
                    total_output_tokens += usage.get('completion_tokens', 0)

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

                    # Track SQL queries for evaluation
                    if tool_name == "QueryDatabase" and "query" in tool_args:
                        sql_queries_executed.append(tool_args["query"])

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

            # Calculate total tokens
            total_tokens = total_input_tokens + total_output_tokens

            return AgentResponse(
                message=Message(role="assistant", content=content),
                usage={
                    "prompt_tokens": total_input_tokens,
                    "completion_tokens": total_output_tokens,
                    "total_tokens": total_tokens
                },
                metadata={
                    "agent_type": "react",
                    "tools_used": [tool.name for tool in self.tools],
                    "iterations": iteration,
                    "sql_queries": sql_queries_executed
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
        temperature: float = 0.7,
        max_tokens: int = 2000,
        enable_visualizations: bool = True,
        **kwargs
    ):
        """Stream response from chat method"""
        response = self.chat(messages, temperature, enable_visualizations=enable_visualizations, **kwargs)
        yield response.message.content

    def get_agent_type(self) -> str:
        return "react"
