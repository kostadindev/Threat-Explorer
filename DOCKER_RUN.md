# Running Threat Explorer with Docker

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t threat-explorer .
```

This will:
- Build the React frontend
- Set up the Python backend
- Copy all necessary files
- Create a production-ready image

### 2. Run the Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -e MODEL=gpt-4o-mini \
  threat-explorer
```

### 3. Access the App

Open your browser and go to:
```
http://localhost:8000
```

## Environment Variables

You can set environment variables when running:

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e MODEL=gpt-4o-mini \
  -e CORS_ORIGINS=* \
  threat-explorer
```

Or use a `.env` file:

```bash
docker run -p 8000:8000 --env-file .env threat-explorer
```

## Using Docker Compose (Optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL=${MODEL:-gpt-4o-mini}
      - CORS_ORIGINS=${CORS_ORIGINS:-*}
    env_file:
      - .env
```

Then run:
```bash
docker-compose up
```

## Common Commands

### Build and run in one command
```bash
docker build -t threat-explorer . && docker run -p 8000:8000 -e OPENAI_API_KEY=your_key threat-explorer
```

### Run in detached mode (background)
```bash
docker run -d -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  --name threat-explorer \
  threat-explorer
```

### View logs
```bash
docker logs threat-explorer
# or follow logs
docker logs -f threat-explorer
```

### Stop the container
```bash
docker stop threat-explorer
```

### Remove the container
```bash
docker rm threat-explorer
```

### Remove the image
```bash
docker rmi threat-explorer
```

## Troubleshooting

### Port already in use
If port 8000 is already in use, use a different port:
```bash
docker run -p 3000:8000 -e OPENAI_API_KEY=your_key threat-explorer
```
Then access at `http://localhost:3000`

### Check if container is running
```bash
docker ps
```

### Check container logs
```bash
docker logs threat-explorer
```

### Access container shell
```bash
docker exec -it threat-explorer /bin/bash
```

### Rebuild after changes
```bash
docker build --no-cache -t threat-explorer .
```

## What Happens on Startup

1. **Database Initialization**: The SQLite database loads from `cybersecurity_attacks.csv`
2. **Backend Starts**: FastAPI server starts on port 8000
3. **Frontend Served**: Built React app is served as static files
4. **Ready**: App is accessible at `http://localhost:8000`

## Notes

- The database is in-memory and loads from CSV on each startup
- All frontend assets are built into the image
- The app runs in production mode
- Environment variables can be set at runtime

