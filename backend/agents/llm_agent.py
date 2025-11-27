from typing import List
import json
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from .base import BaseAgent, Message, AgentResponse
from constants import LLM_AGENT_SYSTEM_PROMPT
from tools.database_tool import query_database, get_database_info


class LLMAgent(BaseAgent):
    """
    LLM agent with function calling support for database queries.
    Uses OpenAI's function calling to query the cybersecurity attacks database.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key
        )
        self.tools = self._get_tool_definitions()

    def _get_tool_definitions(self):
        """Define OpenAI function calling tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_database",
                    "description": """Query the cybersecurity attacks database using SQL. The database contains a table called 'attacks' with fields like: Timestamp, Source IP Address, Destination IP Address, Attack Type, Severity Level, Protocol, Malware Indicators, etc. Column names with spaces must be quoted with double quotes.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute. Example: SELECT * FROM attacks WHERE \"Attack Type\" = 'Malware' LIMIT 5"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_database_info",
                    "description": "Get information about the database schema including table name, columns, and row count. Use this before querying to understand available data.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_arguments: dict) -> str:
        """Execute a tool and return the result"""
        if tool_name == "query_database":
            return query_database(tool_arguments.get("query", ""))
        elif tool_name == "get_database_info":
            return get_database_info()
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using LLM with function calling support.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            AgentResponse with LLM's reply
        """
        print("", flush=True)
        print("=" * 80, flush=True)
        print("🤖 LLM AGENT - FUNCTION CALLING MODE", flush=True)
        print("=" * 80, flush=True)
        print(f"🔧 Available tools: {[tool['function']['name'] for tool in self.tools]}", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)

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

        # Create LLM instance with parameters and tools
        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key
        )

        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(self.tools)

        print("🔄 Sending initial request to LLM...", flush=True)
        # Get initial response
        response = llm_with_tools.invoke(langchain_messages)

        # Check if LLM wants to use tools
        if hasattr(response, "tool_calls") and response.tool_calls:
            print(f"✅ LLM decided to use {len(response.tool_calls)} tool(s)", flush=True)
        else:
            print("ℹ️  LLM decided NOT to use any tools - providing direct response", flush=True)

        # Handle tool calls if present
        tool_calls_made = []
        iteration = 0
        while hasattr(response, "tool_calls") and response.tool_calls:
            iteration += 1
            print("", flush=True)
            print("=" * 80, flush=True)
            print(f"🤖 LLM AGENT - Tool Call Iteration {iteration}", flush=True)
            print(f"📞 Number of tool calls: {len(response.tool_calls)}", flush=True)
            print("=" * 80, flush=True)

            # Add assistant's message with tool calls to history
            langchain_messages.append(response)

            # Execute each tool call
            for idx, tool_call in enumerate(response.tool_calls, 1):
                tool_name = tool_call["name"]
                tool_arguments = tool_call["args"]
                tool_calls_made.append(tool_name)

                print(f"\n🔧 Tool Call #{idx}", flush=True)
                print(f"   Name: {tool_name}", flush=True)
                print(f"   Arguments: {json.dumps(tool_arguments, indent=6)}", flush=True)

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_arguments)

                print(f"   Result length: {len(tool_result)} characters", flush=True)

                # Add tool result to messages
                langchain_messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                )

            print("", flush=True)
            print("🔄 Getting LLM response with tool results...", flush=True)
            # Get next response
            response = llm_with_tools.invoke(langchain_messages)

        if tool_calls_made:
            print("", flush=True)
            print("=" * 80, flush=True)
            print(f"✅ LLM AGENT - Tool calling complete", flush=True)
            print(f"📊 Total tools used: {tool_calls_made}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

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
            metadata={
                "agent_type": "llm",
                "tools_used": tool_calls_made
            }
        )

    def chat_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Process messages using LLM inference with streaming and tool calling support.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of the response as they arrive
        """
        print("", flush=True)
        print("=" * 80, flush=True)
        print("🌊 LLM AGENT - STREAMING MODE WITH TOOL SUPPORT", flush=True)
        print("=" * 80, flush=True)
        print(f"🔧 Available tools: {[tool['function']['name'] for tool in self.tools]}", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)

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

        # Create LLM instance with parameters and tools
        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key,
            streaming=True
        )

        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(self.tools)

        # Handle tool calls in a loop before streaming final response
        tool_calls_made = []
        iteration = 0
        max_iterations = 5  # Prevent infinite loops
        final_response = None

        print("🔄 Checking for tool calls...", flush=True)
        print("", flush=True)

        while iteration < max_iterations:
            iteration += 1
            
            # Make a non-streaming call to check for tool calls
            # This is fast and allows us to execute tools before streaming
            response = llm_with_tools.invoke(langchain_messages)

            # Check if LLM wants to use tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                print("", flush=True)
                print("=" * 80, flush=True)
                print(f"🔧 Tool calls detected (iteration {iteration})", flush=True)
                print(f"📞 Number of tool calls: {len(response.tool_calls)}", flush=True)
                print("=" * 80, flush=True)
                print("", flush=True)

                # Add assistant's message with tool calls to history
                langchain_messages.append(response)

                # Execute each tool call
                for idx, tool_call in enumerate(response.tool_calls, 1):
                    tool_name = tool_call["name"]
                    tool_arguments = tool_call["args"]
                    tool_calls_made.append(tool_name)

                    print(f"\n🔧 Tool Call #{idx}", flush=True)
                    print(f"   Name: {tool_name}", flush=True)
                    print(f"   Arguments: {json.dumps(tool_arguments, indent=6)}", flush=True)

                    # Execute the tool
                    tool_result = self._execute_tool(tool_name, tool_arguments)

                    print(f"   Result length: {len(tool_result)} characters", flush=True)

                    # Add tool result to messages
                    langchain_messages.append(
                        ToolMessage(
                            content=tool_result,
                            tool_call_id=tool_call["id"]
                        )
                    )

                print("", flush=True)
                print("🔄 Getting final response with tool results...", flush=True)
                print("", flush=True)
                # Continue the loop to get the next response
                continue
            else:
                # No tool calls, store this response to stream
                final_response = response
                break

        if tool_calls_made:
            print("", flush=True)
            print("=" * 80, flush=True)
            print(f"✅ Tool execution complete", flush=True)
            print(f"📊 Total tools used: {tool_calls_made}", flush=True)
            print("=" * 80, flush=True)
            print("", flush=True)

        # Now stream the final response after tool execution
        print("🔄 Starting to stream final response chunks...", flush=True)
        print("", flush=True)

        # Stream the final response
        # If we have a response with content, stream it in chunks for better UX
        # Otherwise, make a streaming API call
        chunk_count = 0
        if final_response and final_response.content:
            # Stream the content we already have in chunks
            content = final_response.content
            chunk_size = 30  # Stream in chunks for smooth UX
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                chunk_count += 1
                yield chunk
        elif final_response is None or (final_response and not final_response.content):
            # Make a streaming API call for the final response
            # This handles cases where we don't have a final response yet
            for chunk in llm_with_tools.stream(langchain_messages):
                if chunk.content:
                    chunk_count += 1
                    yield chunk.content
        else:
            # Fallback: yield empty string if we somehow get here
            yield ""

        print("", flush=True)
        print(f"✅ Streaming complete - sent {chunk_count} chunks", flush=True)
        print("", flush=True)

    def get_agent_type(self) -> str:
        return "llm"
