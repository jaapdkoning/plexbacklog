# === FRONTEND BUILD ===
FROM node:20 AS frontend
WORKDIR /app
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# === BACKEND RUNTIME ===
FROM python:3.11-slim
WORKDIR /app

# System packages (optioneel: alleen nodig als je C-extensies nodig hebt)
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY backend/main.py ./main.py
COPY backend/templates ./templates
COPY --from=frontend /app/frontend/dist ./static

# .env wordt geladen op runtime, dus niet kopiëren hier

# Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
