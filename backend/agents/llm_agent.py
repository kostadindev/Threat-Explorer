from typing import List
import json
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from .base import BaseAgent, Message, AgentResponse
from constants import LLM_AGENT_SYSTEM_PROMPT, get_system_prompt
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
                    "description": """Query the cybersecurity attacks database using SQL. The database contains a table called 'attacks' with fields like: Timestamp, Source IP Address, Destination IP Address, Attack Type, Severity Level, Protocol, Malware Indicators, etc. Column names with spaces must be quoted with double quotes. If no LIMIT is specified, a default LIMIT 20 will be applied automatically.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute. Example: SELECT * FROM attacks WHERE \"Attack Type\" = 'Malware' LIMIT 5. If no LIMIT clause is provided, LIMIT 20 will be added automatically."
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
            query = tool_arguments.get("query", "")
            # Add default LIMIT 20 if not specified
            if query and "limit" not in query.lower():
                query = query.rstrip(';').rstrip() + " LIMIT 20"
            return query_database(query)
        elif tool_name == "get_database_info":
            return get_database_info()
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def chat(
        self,
        messages: List[Message],
        temperature: float = 1,
        enable_visualizations: bool = True,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using LLM with function calling support.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            enable_visualizations: Whether to enable database visualizations
            max_tokens: Maximum tokens to generate

        Returns:
            AgentResponse with LLM's reply
        """
        # Extract system prompts and conversation messages separately
        system_prompt = get_system_prompt(LLM_AGENT_SYSTEM_PROMPT, enable_visualizations)
        system_messages = [SystemMessage(content=system_prompt)]
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
            max_tokens=kwargs.get("max_tokens", 10000),
            openai_api_key=self.api_key
        )

        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(self.tools)

        # Get initial response
        response = llm_with_tools.invoke(langchain_messages)

        # Handle tool calls if present
        tool_calls_made = []
        iteration = 0
        while hasattr(response, "tool_calls") and response.tool_calls:
            iteration += 1

            # Add assistant's message with tool calls to history
            langchain_messages.append(response)

            # Execute each tool call
            for idx, tool_call in enumerate(response.tool_calls, 1):
                tool_name = tool_call["name"]
                tool_arguments = tool_call["args"]
                tool_calls_made.append(tool_name)

                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_arguments)

                # Add tool result to messages
                langchain_messages.append(
                    ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    )
                )

            # Get next response
            response = llm_with_tools.invoke(langchain_messages)

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
        enable_visualizations: bool = True,
        **kwargs
    ):
        """
        Process messages using LLM inference with streaming and tool calling support.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            enable_visualizations: Whether to enable database visualizations

        Yields:
            Chunks of the response as they arrive
        """
        # Extract system prompts and conversation messages separately
        system_prompt = get_system_prompt(LLM_AGENT_SYSTEM_PROMPT, enable_visualizations)
        system_messages = [SystemMessage(content=system_prompt)]
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

        while iteration < max_iterations:
            iteration += 1
            
            # Make a non-streaming call to check for tool calls
            # This is fast and allows us to execute tools before streaming
            response = llm_with_tools.invoke(langchain_messages)

            # Check if LLM wants to use tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                # Add assistant's message with tool calls to history
                langchain_messages.append(response)

                # Execute each tool call
                for idx, tool_call in enumerate(response.tool_calls, 1):
                    tool_name = tool_call["name"]
                    tool_arguments = tool_call["args"]
                    tool_calls_made.append(tool_name)

                    # Execute the tool
                    tool_result = self._execute_tool(tool_name, tool_arguments)

                    # Add tool result to messages
                    langchain_messages.append(
                        ToolMessage(
                            content=tool_result,
                            tool_call_id=tool_call["id"]
                        )
                    )

                # Continue the loop to get the next response
                continue
            else:
                # No tool calls, store this response to stream
                final_response = response
                break

        # Now stream the final response after tool execution
        # Stream the final response
        # If we have a response with content, stream it in chunks for better UX
        # Otherwise, make a streaming API call
        if final_response and final_response.content:
            # Stream the content we already have in chunks
            content = final_response.content
            chunk_size = 30  # Stream in chunks for smooth UX
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield chunk
        elif final_response is None or (final_response and not final_response.content):
            # Make a streaming API call for the final response
            # This handles cases where we don't have a final response yet
            for chunk in llm_with_tools.stream(langchain_messages):
                if chunk.content:
                    yield chunk.content
        else:
            # Fallback: yield empty string if we somehow get here
            yield ""

    def get_agent_type(self) -> str:
        return "llm"
