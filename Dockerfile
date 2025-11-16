FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    google-cloud-aiplatform>=1.40.0 \
    google-cloud-storage>=2.10.0 \
    vertexai>=1.0.0 \
    tqdm \
    pyyaml

# Copy script from correct location
COPY scripts/embeddings/generate_embeddings_parallel.py .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "generate_embeddings_parallel.py"]
