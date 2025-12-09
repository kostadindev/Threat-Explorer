from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path


from api import router
from config import config
from db.database import db

# Initialize FastAPI app
app = FastAPI(
    title="Threat Explorer API",
    description="Multi-agent cybersecurity assistant with LLM, ReAct, and Multi-Agent modes",
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

# Serve static files from frontend build
# Path from backend directory: go up one level to /app, then to frontend/dist
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

# Log frontend path for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"Frontend dist path: {frontend_dist}")
logger.info(f"Frontend dist exists: {frontend_dist.exists()}")

if frontend_dist.exists():
    # Mount static assets directory
    static_path = frontend_dist / "assets"
    if static_path.exists():
        app.mount("/assets", StaticFiles(directory=str(static_path)), name="assets")
        logger.info(f"Mounted assets from: {static_path}")
    
    # Serve root path explicitly (must be after router to override API root)
    @app.get("/", include_in_schema=False)
    async def serve_root():
        """Serve the React app at root"""
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"error": "Frontend index.html not found", "path": str(index_path)}
    
    # Serve index.html for all non-API routes (SPA routing)
    # This must be last to not interfere with API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React app for all non-API routes"""
        # Skip if it's an API route or static asset (shouldn't happen due to route order, but safety check)
        if full_path in ("health", "ping") or full_path.startswith(("api/", "chat", "suggest-followups", "query", "db/", "assets/")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Check if it's a static file first (like vite.svg)
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file() and full_path != "index.html":
            return FileResponse(str(file_path))
        
        # Otherwise serve index.html for SPA routing
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        logger.error(f"Frontend not found at: {index_path}")
        return {"error": "Frontend not found", "path": str(index_path), "frontend_dist": str(frontend_dist)}
else:
    logger.warning(f"Frontend dist directory not found at: {frontend_dist}")


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""


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
