from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from config import config

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
