# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# === BACKEND RUNTIME ===
FROM python:3.11-slim
WORKDIR /app

# Install dependencies early
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend ./backend

# Copy built frontend into static folder
COPY --from=frontend /app/frontend/dist /app/static

# Define environment variables (override in .env or docker-compose)
ENV RADARR_URL=... \
    RADARR_API=... \
    SONARR_URL=... \
    SONARR_API=... \
    LIDARR_URL=... \
    LIDARR_API=...

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
