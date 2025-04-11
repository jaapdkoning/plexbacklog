# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# === BACKEND RUNTIME ===
FROM python:3.11-slim

RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && \
    pip install --upgrade pip

WORKDIR /app

# Backend en templates
COPY backend /app/backend
COPY backend/templates /app/templates

# requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Static files vanuit frontend
COPY --from=frontend /app/frontend/dist /app/static

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]
