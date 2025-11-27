from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from config import config
from db.database import db

# Initialize FastAPI app
app = FastAPI(
    title="Threat Explorer API",
    description="Multi-agent cybersecurity assistant with LLM, ReACT, and Multi-Agent modes",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    import logging
    logger = logging.getLogger(__name__)

    logger.info("")
    logger.info("=" * 80)
    logger.info("🚀 THREAT EXPLORER API STARTING")
    logger.info("=" * 80)
    logger.info("")

    db.initialize()

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ THREAT EXPLORER API READY")
    logger.info(f"📡 Server: {config.HOST}:{config.PORT}")
    logger.info(f"🤖 Available agents: llm, react, multi")
    logger.info("=" * 80)
    logger.info("")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connection on application shutdown"""
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
