# Backend API Server

FastAPI backend for RAG-Frontend integration.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with:
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GCP_PROJECT_ID=428461461446
GCP_LOCATION=europe-west1
```

3. Ensure `metadata_store_production.pkl` exists in the parent directory

## Running

Start the server:
```bash
python api_server.py
```

Server will run on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## Endpoints

- `GET /` - Health check
- `POST /api/regulations` - Get regulations for a subcategory
- `POST /api/analyze` - Analyze overlaps and contradictions
- `GET /api/cache/stats` - Get cache statistics
- `DELETE /api/cache` - Clear all cached data

## Caching

The backend uses SQLite to cache generated responses, dramatically improving performance for repeated queries:

- **Regulations cache**: Stores RAG search results by subcategory
- **Analysis cache**: Stores LLM-generated overlaps and contradictions
- **Automatic**: Cache is checked before every query and populated after generation
- **Persistent**: Cache survives server restarts
- **Database**: `backend/rag_cache.db` (auto-created on first run)

### Cache Benefits

- Instant responses for previously queried subcategories
- Reduced API costs (no repeated LLM calls)
- Consistent results for the same query
- Access tracking for analytics

### Cache Management

View cache statistics:
```bash
curl http://localhost:8000/api/cache/stats
```

Clear cache:
```bash
curl -X DELETE http://localhost:8000/api/cache
```
