# RAG System API Guide

## Overview

The RAG (Retrieval-Augmented Generation) system provides semantic search over 225,168 EU legislation chunks with metadata. It combines vector similarity search with optional LLM analysis to find regulatory overlaps and contradictions.

## System Components

**Vector Index**: 274,300 embeddings in europe-west1
**Metadata Store**: 225,168 records with full text, regulation names, articles, years
**Embedding Model**: text-multilingual-embedding-002 (768 dimensions)
**LLM**: gemini-2.5-pro (for analysis)

## Core Functionality

### 1. Basic Search

```python
from rag_search import EULegislationRAG

rag = EULegislationRAG(
    project_id="428461461446",
    location="europe-west1",
    index_endpoint_name="projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912",
    deployed_index_id="eu_legislation_prod_75480320",
    metadata_file="metadata_store_production.pkl"
)

result = rag.query(
    user_query="data protection requirements",
    top_k=10,
    analyze_with_llm=False
)
```

**Returns**:
```python
{
    'query': str,
    'num_results': int,
    'top_chunks': [
        {
            'score': float,  # similarity score
            'id': str,
            'metadata': {
                'regulation_name': str,
                'article_number': str,
                'year': int,
                'doc_type': str,
                'full_text': str,
                'paragraph_numbers': list
            }
        }
    ],
    'llm_analysis': str | None
}
```

### 2. Advanced Search with Filters

```python
result = rag.query(
    user_query="banking capital requirements",
    risk_category="financial_regulation",  # keyword filter
    year_filter=2020,  # only regulations from 2020+
    top_k=20,
    analyze_with_llm=False,
    use_query_expansion=True  # generates query variations
)
```

**Risk Categories**:
- `data_privacy` - GDPR, personal data, ePrivacy
- `financial_regulation` - MiFID, Basel, banking
- `consumer_protection` - consumer rights, contracts
- `environmental` - emissions, sustainability
- `aml_cft` - money laundering, terrorist financing
- `payments` - payment services, PSD2
- `insurance` - Solvency, reinsurance
- (15 total categories)

### 3. LLM Analysis for Contradictions

```python
result = rag.query(
    user_query="payment service provider licensing requirements",
    top_k=30,
    analyze_with_llm=True,  # enable Gemini analysis
    focus_cross_regulation=True  # only flag cross-regulation issues
)

# Access analysis
print(result['llm_analysis'])
```

**LLM Analysis Output**:
- SUMMARY - Overview of findings
- KEY FINDINGS - Numbered list of important points
- CONTRADICTIONS - Conflicts between different regulations
- OVERLAPS - Overlapping regulatory scope
- RECOMMENDATIONS - Actionable compliance insights

Each finding includes:
- Regulation name + Article citation
- Relevant text quote
- Explanation of overlap/contradiction
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Practical impact for compliance

### 4. Query Expansion (Better Recall)

```python
result = rag.query(
    user_query="customer due diligence",
    use_query_expansion=True,  # generates 2 alternative phrasings
    top_k=50
)
```

Uses Reciprocal Rank Fusion (RRF) to combine results from multiple query variations for better coverage.

## Frontend Integration Pattern

### REST API Wrapper (Recommended)

Create a FastAPI/Flask endpoint:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_search import EULegislationRAG

app = FastAPI()

# Initialize once at startup
rag = EULegislationRAG(
    project_id="428461461446",
    location="europe-west1",
    index_endpoint_name="projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912",
    deployed_index_id="eu_legislation_prod_75480320"
)

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    risk_category: str | None = None
    year_filter: int | None = None
    analyze_with_llm: bool = False

@app.post("/api/search")
async def search(request: SearchRequest):
    try:
        result = rag.query(
            user_query=request.query,
            top_k=request.top_k,
            risk_category=request.risk_category,
            year_filter=request.year_filter,
            analyze_with_llm=request.analyze_with_llm,
            use_query_expansion=True
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-contradictions")
async def analyze_contradictions(request: SearchRequest):
    result = rag.query(
        user_query=request.query,
        top_k=30,
        analyze_with_llm=True,
        focus_cross_regulation=True
    )
    return {
        'query': result['query'],
        'analysis': result['llm_analysis'],
        'source_chunks': result['top_chunks'][:5]
    }
```

### Frontend Usage

```typescript
// Search for regulations
const searchRegulations = async (query: string) => {
  const response = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      top_k: 10,
      analyze_with_llm: false
    })
  });
  return await response.json();
};

// Find contradictions
const findContradictions = async (query: string) => {
  const response = await fetch('/api/analyze-contradictions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      top_k: 30
    })
  });
  return await response.json();
};
```

## Performance Characteristics

- **Search latency**: ~500ms for top-10 results
- **With query expansion**: ~1.5s (3 queries + RRF)
- **With LLM analysis**: +3-5s (depends on Gemini response time)
- **Metadata lookup**: ~10ms per result

## Cost Estimates

- **Vector search**: ~$0.15 per 1,000 queries
- **Embeddings**: $0.025 per 1,000 queries (text-multilingual-embedding-002)
- **LLM analysis**: ~$0.01 per query (Gemini 2.5 Pro)

## Example Use Cases

### 1. Compliance Check
```python
result = rag.query(
    "What are the requirements for storing customer financial data?",
    risk_category="data_privacy",
    year_filter=2018,  # post-GDPR
    analyze_with_llm=True
)
```

### 2. Regulatory Overlap Detection
```python
result = rag.query(
    "payment service provider authorization requirements",
    top_k=50,
    analyze_with_llm=True,
    focus_cross_regulation=True  # only cross-regulation conflicts
)
```

### 3. Quick Reference Lookup
```python
result = rag.query(
    "MiFID II transaction reporting obligations",
    top_k=5,
    analyze_with_llm=False,
    use_query_expansion=False  # faster
)
```

## Error Handling

```python
try:
    result = rag.query(user_query="test")
except gcp_exceptions.ResourceExhausted:
    # Quota exceeded - automatic retry with backoff
    pass
except Exception as e:
    # Handle other errors
    print(f"Search failed: {e}")
```

## Command Line Usage

```bash
# Basic search
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912" \
  --deployed-index-id "eu_legislation_prod_75480320" \
  --query "data protection requirements" \
  --top-k 10 \
  --no-llm

# With filters
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912" \
  --deployed-index-id "eu_legislation_prod_75480320" \
  --query "banking regulations" \
  --risk-category financial_regulation \
  --year-filter 2020 \
  --top-k 20

# With LLM analysis
python rag_search.py \
  --index-endpoint "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912" \
  --deployed-index-id "eu_legislation_prod_75480320" \
  --query "payment service licensing" \
  --top-k 30 \
  --no-query-expansion
```

## Next Steps for Frontend Integration

1. **Create FastAPI backend** with `/api/search` and `/api/analyze-contradictions` endpoints
2. **Add authentication** if needed (API keys, OAuth)
3. **Implement caching** for common queries (Redis)
4. **Add rate limiting** to control costs
5. **Stream LLM responses** for better UX (use Gemini streaming API)
6. **Add query history** to track user searches
7. **Implement feedback loop** to improve results over time
