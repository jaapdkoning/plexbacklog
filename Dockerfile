# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# === BACKEND RUNTIME ===
FROM python:3.11-slim

# Install pip dependencies
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Copy backend code
COPY backend ./backend
COPY templates ./templates
COPY requirements.txt .  # <= uit root directory
COPY --from=frontend /app/frontend/dist /app/static

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment vars (override via .env or compose)
ENV RADARR_URL= RADARR_API_KEY= \
    SONARR_URL= SONARR_API_KEY= \
    LIDARR_URL= LIDARR_API_KEY=

# Run FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
