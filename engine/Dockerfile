# Motor de El Enjambre — imagen para Render/Railway/Fly
FROM python:3.11-slim

# Usuario no-root (defensa en profundidad: el proceso web nunca corre como root).
RUN useradd --create-home --uid 10001 enjambre

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# La base (SQLite) y la caché de cerebros viven bajo /app: el usuario no-root
# debe poder escribir. Si en Render montas un disco persistente en /app/datos,
# asegúrate de que sea escribible por el uid 10001 (ver docs/despliegue.md).
RUN mkdir -p /app/datos /app/brains/cache && chown -R enjambre:enjambre /app
USER enjambre

# Render inyecta $PORT; 8000 como valor por defecto local
ENV PORT=8000
CMD uvicorn server:app --host 0.0.0.0 --port $PORT
