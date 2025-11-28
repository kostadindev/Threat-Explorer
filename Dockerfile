# Multi-stage Dockerfile for Threat Explorer
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ .

# Build frontend
RUN npm run build

# Stage 2: Python backend with built frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy database CSV
COPY backend/db/cybersecurity_attacks.csv ./backend/db/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy MCP server files
COPY backend/mcp/ ./backend/mcp/
COPY mcp_config.json ./

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV HOST=0.0.0.0

# Expose port
EXPOSE 8000

# Run the application (use PORT from environment, default to 8000)
# Use shell form to allow environment variable expansion
CMD sh -c "cd /app/backend && python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

