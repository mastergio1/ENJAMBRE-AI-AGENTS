# Motor de El Enjambre — imagen para Render/Railway/Fly
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render inyecta $PORT; 8000 como valor por defecto local
ENV PORT=8000
CMD uvicorn server:app --host 0.0.0.0 --port $PORT
