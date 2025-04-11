# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === BACKEND RUNTIME ===
FROM python:3.11-slim
WORKDIR /app
COPY backend ./backend
COPY --from=frontend /app/frontend/dist /app/static
RUN pip install fastapi uvicorn httpx
ENV RADARR_URL=... RADARR_API=... SONARR_URL=... SONARR_API=... LIDARR_URL=... LIDARR_API=...
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
