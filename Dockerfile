# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FastAPI and uvicorn
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-multipart

# Copy backend files
COPY api_server.py .
COPY cache_db.py .
COPY config.yaml .

# Copy scripts directory (needed for rag_search imports)
COPY scripts/ ./scripts/

# Copy metadata store
COPY metadata_store_all.pkl .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Expose port
EXPOSE 8080

# Run the application
CMD exec uvicorn api_server:app --host 0.0.0.0 --port ${PORT}
