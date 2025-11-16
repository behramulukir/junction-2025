# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/api_server.py .
COPY backend/cache_db.py .
COPY backend/rag_cache.db .

# Copy files needed by api_server
COPY backend/rag_search.py .
COPY backend/metadata_store_production.pkl .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD exec uvicorn api_server:app --host 0.0.0.0 --port ${PORT}
