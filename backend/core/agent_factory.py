from agents import LLMAgent, ReActAgent, MultiAgent
from config import config


def get_agent():
    """
    Factory function to get the configured agent.

    Returns:
        BaseAgent: An instance of the configured agent type (LLM, ReAct, or Multi-Agent)

    Raises:
        ValueError: If the configured agent type is unknown
    """
    agents = {
        "llm": LLMAgent,
        "react": ReActAgent,
        "multi": MultiAgent,
    }

    if config.AGENT_TYPE not in agents:
        raise ValueError(f"Unknown agent type: {config.AGENT_TYPE}")

    return agents[config.AGENT_TYPE](
        api_key=config.OPENAI_API_KEY,
        model=config.MODEL
    )
