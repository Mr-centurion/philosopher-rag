FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run ingestion during build to warm up vector store
RUN python run_ingest.py

EXPOSE 8000

ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
