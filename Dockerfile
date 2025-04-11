# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# === BACKEND RUNTIME ===
FROM python:3.11-slim
WORKDIR /app
COPY backend ./backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Voeg frontend build toe
COPY --from=frontend /app/frontend/dist ./static

EXPOSE 80
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
