import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # Agent Configuration
    AGENT_TYPE = os.getenv("AGENT_TYPE", "llm")  # Options: "llm", "react", "multi"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("MODEL", "gpt-4o-mini")

    # Server Configuration
    # Heroku sets PORT dynamically, so we need to read it
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


config = Config()
