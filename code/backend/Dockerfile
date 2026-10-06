FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY ml_core /app/ml_core
RUN pip install --no-cache-dir /app/ml_core

COPY backend /app/backend

RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app

WORKDIR /app/backend
USER appuser

ENV ENV=production \
    DATABASE_URL=sqlite:////app/data/fluxora.db \
    MODEL_PATH=/app/data/fluxora_model.joblib

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
