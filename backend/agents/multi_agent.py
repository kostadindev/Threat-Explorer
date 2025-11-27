from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .base import BaseAgent, Message, AgentResponse
from constants import (
    THREAT_ANALYST_SYSTEM_PROMPT,
    DEFENSE_SPECIALIST_SYSTEM_PROMPT,
    COMPLIANCE_EXPERT_SYSTEM_PROMPT,
    GENERAL_SECURITY_SYSTEM_PROMPT,
    SPECIALIST_KEYWORDS
)


class MultiAgent(BaseAgent):
    """
    Multi-agent system that coordinates multiple specialized agents.
    Routes queries to appropriate specialists and synthesizes responses.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key
        )
        self.specialists = self._create_specialists()

    def _create_specialists(self) -> Dict[str, Dict[str, Any]]:
        """Create specialized sub-agents"""
        return {
            "threat_analyst": {
                "name": "Threat Analysis Specialist",
                "system_prompt": THREAT_ANALYST_SYSTEM_PROMPT,
                "keywords": SPECIALIST_KEYWORDS["threat_analyst"]
            },
            "defense_specialist": {
                "name": "Defense & Mitigation Specialist",
                "system_prompt": DEFENSE_SPECIALIST_SYSTEM_PROMPT,
                "keywords": SPECIALIST_KEYWORDS["defense_specialist"]
            },
            "compliance_expert": {
                "name": "Compliance & Policy Expert",
                "system_prompt": COMPLIANCE_EXPERT_SYSTEM_PROMPT,
                "keywords": SPECIALIST_KEYWORDS["compliance_expert"]
            },
            "general_security": {
                "name": "General Security Advisor",
                "system_prompt": GENERAL_SECURITY_SYSTEM_PROMPT,
                "keywords": []  # Default fallback
            }
        }

    def _route_to_specialist(self, query: str) -> str:
        """Determine which specialist should handle the query"""
        query_lower = query.lower()

        # Score each specialist based on keyword matches
        scores = {}
        for specialist_id, specialist in self.specialists.items():
            if not specialist["keywords"]:  # Skip general (fallback)
                continue
            score = sum(1 for keyword in specialist["keywords"] if keyword in query_lower)
            scores[specialist_id] = score

        # Return specialist with highest score, or general if no matches
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general_security"

    def _consult_specialist(
        self,
        specialist_id: str,
        query: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Get response from a specific specialist"""
        specialist = self.specialists[specialist_id]

        messages = [
            SystemMessage(content=specialist["system_prompt"]),
            HumanMessage(content=query)
        ]

        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key
        )

        response = llm.invoke(messages)
        return response.content

    def _synthesize_response(
        self,
        query: str,
        specialist_responses: Dict[str, str],
        temperature: float,
        max_tokens: int
    ) -> tuple[str, dict]:
        """Synthesize multiple specialist responses into a coherent answer"""

        if len(specialist_responses) == 1:
            # Only one specialist consulted, return their response directly
            specialist_name = list(specialist_responses.keys())[0]
            response_text = list(specialist_responses.values())[0]
            return response_text, {"primary_specialist": specialist_name}

        # Multiple specialists - synthesize their insights
        synthesis_prompt = f"""Given the following expert opinions on the question: "{query}"

"""
        for specialist, response in specialist_responses.items():
            synthesis_prompt += f"\n{self.specialists[specialist]['name']}:\n{response}\n"

        synthesis_prompt += "\nSynthesize these expert opinions into a comprehensive, coherent answer. Highlight key points from each specialist and resolve any contradictions."

        messages = [
            SystemMessage(content="You are a coordinator synthesizing expert opinions."),
            HumanMessage(content=synthesis_prompt)
        ]

        llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key
        )

        response = llm.invoke(messages)

        usage = {}
        if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
            token_usage = response.response_metadata["token_usage"]
            usage = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

        return response.content, usage

    def chat(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AgentResponse:
        """
        Process messages using multi-agent coordination.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Can include 'consult_all' to get input from all specialists

        Returns:
            AgentResponse with synthesized multi-agent reply
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
                metadata={"agent_type": "multi", "error": "No user input"}
            )

        try:
            consult_all = kwargs.get("consult_all", False)
            specialist_responses = {}

            if consult_all:
                # Consult all specialists
                for specialist_id in self.specialists.keys():
                    response = self._consult_specialist(
                        specialist_id,
                        user_message,
                        temperature,
                        max_tokens
                    )
                    specialist_responses[specialist_id] = response
            else:
                # Route to best specialist
                specialist_id = self._route_to_specialist(user_message)
                response = self._consult_specialist(
                    specialist_id,
                    user_message,
                    temperature,
                    max_tokens
                )
                specialist_responses[specialist_id] = response

            # Synthesize responses
            final_response, usage = self._synthesize_response(
                user_message,
                specialist_responses,
                temperature,
                max_tokens
            )

            return AgentResponse(
                message=Message(role="assistant", content=final_response),
                usage=usage,
                metadata={
                    "agent_type": "multi",
                    "specialists_consulted": list(specialist_responses.keys()),
                    "routing_mode": "all" if consult_all else "routed"
                }
            )

        except Exception as e:
            return AgentResponse(
                message=Message(
                    role="assistant",
                    content=f"I encountered an error while coordinating the specialists: {str(e)}"
                ),
                usage={},
                metadata={"agent_type": "multi", "error": str(e)}
            )

    def get_agent_type(self) -> str:
        return "multi"
