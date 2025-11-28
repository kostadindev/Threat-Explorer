# Quick Docker Deployment

## One-Command Deploy

```bash
docker build -t threat-explorer . && docker run -p 8000:8000 -e OPENAI_API_KEY=your_key threat-explorer
```

## What's Included

✅ **Full-stack app**: Frontend + Backend in one container
✅ **Database**: Auto-loads on startup
✅ **MCP Support**: MCP server files included
✅ **Production-ready**: Optimized build process

## Files Created

- `Dockerfile` - Multi-stage build for frontend + backend
- `.dockerignore` - Excludes unnecessary files
- `DEPLOY.md` - Full deployment guide

## Environment Variables

Set these when running:
- `OPENAI_API_KEY` (required)
- `MODEL` (optional, default: gpt-4o-mini)
- `CORS_ORIGINS` (optional, default: *)
- `PORT` (optional, default: 8000)

## Testing Locally

```bash
docker build -t threat-explorer .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key threat-explorer
```

Visit http://localhost:8000

## Running in Background

```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  --name threat-explorer \
  threat-explorer
```

## View Logs

```bash
docker logs -f threat-explorer
```

## Stop Container

```bash
docker stop threat-explorer
docker rm threat-explorer
```
