# Deployment Guide with Docker

This guide explains how to deploy Threat Explorer using Docker.

## Prerequisites

1. Docker installed
2. OpenAI API key

## Quick Deploy

### 1. Build the Docker Image

```bash
docker build -t threat-explorer .
```

### 2. Run the Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e MODEL=gpt-4o-mini \
  threat-explorer
```

### 3. Access Your App

Open your browser to `http://localhost:8000`

## What Gets Deployed

The Dockerfile creates a multi-stage build that:

1. **Builds the Frontend**: Compiles the React/TypeScript frontend into static files
2. **Sets up Python Backend**: Installs all Python dependencies
3. **Loads Database**: Copies the cybersecurity_attacks.csv file
4. **Serves Everything**: FastAPI serves both the API and the static frontend files

## Features Included

✅ **Backend API**: FastAPI server with all agent types (LLM, ReACT, Multi-Agent)
✅ **Frontend**: Built React app served as static files
✅ **Database**: SQLite database loaded from CSV on startup
✅ **MCP Support**: MCP server files included (can be run separately if needed)
✅ **Auto-initialization**: Database loads automatically on startup

## Environment Variables

Set these when running the container:

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `MODEL` (optional): Model to use (default: gpt-4o-mini)
- `CORS_ORIGINS` (optional): Comma-separated list of allowed origins (default: *)
- `PORT` (optional): Port to run on (default: 8000)
- `HOST` (optional): Host to bind to (default: 0.0.0.0)

## Using a Different Port

```bash
docker run -p 3000:8000 \
  -e OPENAI_API_KEY=your_key \
  threat-explorer
```

Then access at `http://localhost:3000`

## Running in Background

```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  --name threat-explorer \
  threat-explorer
```

View logs:
```bash
docker logs -f threat-explorer
```

## Troubleshooting

### Database not loading
- Check that `backend/db/cybersecurity_attacks.csv` exists
- Check logs: `docker logs <container-id>`

### Frontend not showing
- Check that frontend was built: `docker build` should show "frontend-builder" stage
- Verify static files are mounted in `backend/main.py`
- Check logs for frontend path errors

### MCP not working
- MCP server files are included but may need to be run separately
- Check `backend/mcp/database_server.py` for MCP server implementation

## Updating the App

To update after making changes:

```bash
# Rebuild the image
docker build -t threat-explorer .

# Stop and remove old container
docker stop threat-explorer
docker rm threat-explorer

# Run new container
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key threat-explorer
```

## Notes

- The app uses an in-memory SQLite database that loads from CSV on each startup
- For production, consider using a persistent database
- The frontend uses relative URLs, so it works on any domain
- All API routes are prefixed and won't conflict with frontend routing
