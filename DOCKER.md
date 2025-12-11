# Docker Setup Guide

## Super Easy Setup (Docker Compose)

### Step 1: Get Your OpenAI API Key
Get your API key from: https://platform.openai.com/api-keys

### Step 2: Set Up Environment Variables
```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 3: Run with Docker Compose
```bash
# From the main project directory
cd ..
docker-compose up
```

That's it! The app will be available at: http://localhost:8000

---

## Alternative: Docker Only (No Compose)

### Build the Image
```bash
docker build -t threat-explorer .
```

### Run the Container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-api-key-here \
  -e MODEL=gpt-4o-mini \
  threat-explorer
```

---

## What Gets Built

1. **Frontend**: React + Vite app (built to `frontend/dist`)
2. **Backend**: FastAPI server that serves both:
   - REST API endpoints (`/api/*`)
   - Static frontend files (everything else)

The backend runs on port 8000 and serves the entire application.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `HOST` | No | `0.0.0.0` | Server host |
| `PORT` | No | `8000` | Server port |
| `CORS_ORIGINS` | No | `*` | Comma-separated CORS origins |

---

## Useful Commands

### View Logs
```bash
# With docker-compose:
docker-compose logs -f

# Or with docker directly:
docker logs -f threat-explorer
```

### Stop the Application
```bash
# With docker-compose:
docker-compose down

# Or with docker directly:
docker stop threat-explorer
```

### Rebuild After Code Changes
```bash
# With docker-compose:
docker-compose up --build

# Or with docker directly:
docker build -t threat-explorer .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key threat-explorer
```

### Access Container Shell
```bash
docker exec -it threat-explorer /bin/bash
```

---

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, edit `docker-compose.yml` and change:
```yaml
ports:
  - "8001:8000"  # Use port 8001 instead
```

Or with Docker directly:
```bash
docker run -p 8001:8000 -e OPENAI_API_KEY=your-key threat-explorer
```

### Frontend Not Loading
Make sure the frontend build completed successfully:
```bash
docker-compose build --no-cache
# Or:
docker build --no-cache -t threat-explorer .
```

### API Errors
Check your OPENAI_API_KEY is set correctly in `backend/.env`:
```bash
cat backend/.env
```

---

## Development Mode

For development with hot-reload, it's better to run frontend and backend separately:

### Frontend (Terminal 1)
```bash
cd frontend
npm install
npm run dev
```

### Backend (Terminal 2)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## Production Deployment

For production, you can deploy the Docker image to:
- **Heroku**: Use the Dockerfile
- **AWS ECS/Fargate**: Upload to ECR and deploy
- **Google Cloud Run**: Deploy container directly
- **DigitalOcean App Platform**: Connect your repo

Make sure to:
1. Set `OPENAI_API_KEY` as an environment variable (not in .env file)
2. Set appropriate `CORS_ORIGINS` for your domain
3. Use HTTPS in production

---

## Need Help?

1. Check the logs: `docker-compose logs -f`
2. Verify your .env file: `cat backend/.env`
3. Rebuild from scratch: `docker-compose down && docker-compose up --build`
