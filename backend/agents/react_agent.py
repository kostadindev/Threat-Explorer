from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun

from .base import BaseAgent, Message, AgentResponse
from constants import (
    REACT_AGENT_SYSTEM_PROMPT,
    SEARCH_TOOL_DESCRIPTION,
    THREAT_ANALYSIS_TOOL_DESCRIPTION,
    THREAT_SEVERITY_KEYWORDS
)


class ReACTAgent(BaseAgent):
    """
    ReACT (Reasoning + Acting) agent that can use tools.
    Uses a thought-action-observation loop to solve problems.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            temperature=0  # ReACT works better with low temperature
        )
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()

    def _create_tools(self) -> List[Tool]:
        """Create tools for the ReACT agent to use"""

        # Search tool
        search = DuckDuckGoSearchRun()

        tools = [
            Tool(
                name="Search",
                func=search.run,
                description=SEARCH_TOOL_DESCRIPTION
            ),
            Tool(
                name="ThreatAnalysis",
                func=self._analyze_threat,
                description=THREAT_ANALYSIS_TOOL_DESCRIPTION
            ),
        ]

        return tools

    def _analyze_threat(self, threat_description: str) -> str:
        """Simple threat analysis tool"""
        # This is a placeholder - in production, this could call a real threat intelligence API
        threat_lower = threat_description.lower()
        severity = "unknown"

        for level, keywords in THREAT_SEVERITY_KEYWORDS.items():
            if any(keyword in threat_lower for keyword in keywords):
                severity = level
                break

        return f"Threat Analysis: Severity Level - {severity.upper()}. This assessment is based on common threat patterns. For detailed analysis, consult security professionals."

    def _create_agent(self) -> AgentExecutor:
        """Create the ReACT agent executor"""

        # ReACT prompt template
        template = f"""{REACT_AGENT_SYSTEM_PROMPT}

Answer the following question as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using ReACT reasoning loop.

        Args:
            messages: Conversation history
            temperature: Sampling temperature (note: ReACT uses low temp internally)
            max_tokens: Maximum tokens to generate

        Returns:
            AgentResponse with agent's reply including reasoning steps
        """
        # Extract system prompts and user messages separately
        system_prompts = []
        user_message = None

        for msg in messages:
            if msg.role == "system":
                system_prompts.append(msg.content)

        # Get the last user message as the main query
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break

        if not user_message:
            return AgentResponse(
                message=Message(role="assistant", content="No user message found."),
                usage={},
                metadata={"agent_type": "react", "error": "No user input"}
            )

        try:
            # Run the agent
            result = self.agent_executor.invoke({"input": user_message})

            return AgentResponse(
                message=Message(role="assistant", content=result["output"]),
                usage={},  # ReACT agent doesn't expose token usage directly
                metadata={
                    "agent_type": "react",
                    "tools_used": [tool.name for tool in self.tools],
                    "iterations": "max_5"
                }
            )
        except Exception as e:
            return AgentResponse(
                message=Message(
                    role="assistant",
                    content=f"I encountered an error while processing your request: {str(e)}"
                ),
                usage={},
                metadata={"agent_type": "react", "error": str(e)}
            )

    def get_agent_type(self) -> str:
        return "react"
