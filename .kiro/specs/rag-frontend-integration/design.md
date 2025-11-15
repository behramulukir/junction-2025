# Design Document

## Overview

This design integrates the existing React frontend with the Python RAG system through a FastAPI backend. The architecture follows a three-tier pattern: Frontend (React/TypeScript) → Backend API (FastAPI/Python) → RAG System (Google Cloud Vertex AI).

The key design decision is to create a lightweight FastAPI wrapper around the existing `rag_search.py` module rather than rewriting the RAG logic. This minimizes development time and leverages the already-working vector search implementation.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  - Displays risk categories and subcategories                │
│  - Makes API calls to backend                                │
│  - Renders regulations, overlaps, contradictions             │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/JSON
                 │ (CORS enabled)
┌────────────────▼────────────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
│  - /api/regulations - Get regulations for subcategory        │
│  - /api/analyze - Get overlaps & contradictions              │
│  - Transforms RAG results to frontend format                 │
└────────────────┬────────────────────────────────────────────┘
                 │ Python function calls
┌────────────────▼────────────────────────────────────────────┐
│              RAG System (rag_search.py)                      │
│  - EULegislationRAG.query()                                  │
│  - Vector search + LLM analysis                              │
│  - Returns regulation chunks with metadata                   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│         Google Cloud Vertex AI                               │
│  - Matching Engine (vector search)                           │
│  - Gemini 2.5 Pro (LLM analysis)                             │
│  - Text Embedding Model                                      │
└──────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Backend API Server (`backend/api_server.py`)

**Purpose**: FastAPI application that exposes REST endpoints for the frontend

**Key Endpoints**:

```python
POST /api/regulations
Request: {
  "subcategory_id": "1.1",
  "subcategory_description": "Credit assessment and underwriting...",
  "top_k": 10
}
Response: {
  "regulations": [
    {
      "id": "chunk_12345",
      "name": "CRR Article 124",
      "similarityScore": 0.94,
      "description": "Requirements for calculating risk weights...",
      "metadata": {
        "article_number": "124",
        "year": 2013,
        "full_text": "..."
      }
    }
  ]
}

POST /api/analyze
Request: {
  "subcategory_id": "1.1",
  "subcategory_description": "Credit assessment and underwriting...",
  "top_k": 30
}
Response: {
  "overlaps": [
    {
      "id": "overlap-1",
      "regulationPair": ["CRR Article 124", "CRD IV Article 79"],
      "type": "Complementary",
      "description": "Both address credit risk...",
      "confidenceScore": 0.89,
      "excerpts": {
        "regulation1": "Credit institutions shall...",
        "regulation2": "Competent authorities shall..."
      }
    }
  ],
  "contradictions": [
    {
      "id": "contradiction-1",
      "regulationPair": ["CRR Article 124", "Local Banking Act"],
      "description": "Conflicting thresholds...",
      "severity": "Medium",
      "conflictingRequirements": {
        "regulation1": "Risk weight shall not be lower than 35%",
        "regulation2": "Minimum risk weight of 25%"
      }
    }
  ]
}
```

**Dependencies**:
- FastAPI for web framework
- Pydantic for request/response validation
- CORS middleware for frontend access
- Existing `rag_search.py` module

### 2. RAG Integration Layer

**Purpose**: Transform RAG system outputs into frontend-compatible format

**Key Functions**:

```python
def format_regulations(rag_results: dict) -> list[dict]:
    """Convert RAG chunks to frontend Regulation format"""
    
def parse_llm_analysis(llm_text: str) -> tuple[list[dict], list[dict]]:
    """Extract overlaps and contradictions from LLM analysis text"""
    
def generate_unique_id(regulation_pair: tuple) -> str:
    """Create consistent IDs for overlaps/contradictions"""
```

**Design Decision**: The LLM analysis returns structured text with clear sections (SUMMARY, KEY FINDINGS, CONTRADICTIONS, OVERLAPS, RECOMMENDATIONS). We'll parse by:
1. Split text on section headers (e.g., "## CONTRADICTIONS")
2. Extract regulation names from citations (e.g., "CRR Article 124")
3. Extract severity from keywords (CRITICAL/HIGH/MEDIUM/LOW)
4. Parse numbered findings within each section
5. Extract quoted text for excerpts

This is straightforward string parsing, not complex regex.

### 3. Frontend API Client (`frontend/src/api/ragApi.ts`)

**Purpose**: TypeScript client for making API calls from React components

```typescript
export async function fetchRegulations(
  subcategoryId: string,
  description: string,
  topK: number = 10
): Promise<Regulation[]>

export async function fetchAnalysis(
  subcategoryId: string,
  description: string,
  topK: number = 30
): Promise<{ overlaps: Overlap[], contradictions: Contradiction[] }>
```

### 4. Frontend Data Integration

**Purpose**: Replace mock data with API calls in React components

**Changes Required**:
- Remove `import { mockRiskCategories } from './data/mockData'`
- Add API calls when subcategory is selected
- Show loading states during API requests
- Handle error states if API fails

## Data Models

### Backend Pydantic Models

```python
class RegulationRequest(BaseModel):
    subcategory_id: str
    subcategory_description: str
    top_k: int = 10

class AnalysisRequest(BaseModel):
    subcategory_id: str
    subcategory_description: str
    top_k: int = 30

class RegulationResponse(BaseModel):
    id: str
    name: str
    similarityScore: float
    description: str
    metadata: dict

class OverlapResponse(BaseModel):
    id: str
    regulationPair: tuple[str, str]
    type: str  # Duplicate | Complementary | Conflicting
    description: str
    confidenceScore: float
    excerpts: dict

class ContradictionResponse(BaseModel):
    id: str
    regulationPair: tuple[str, str]
    description: str
    severity: str  # High | Medium | Low
    conflictingRequirements: dict
```

## Error Handling

### Backend Error Handling

1. **RAG System Failures**: Catch exceptions from `rag.query()` and return 500 with error message
2. **Empty Results**: Return 200 with empty arrays (valid response)
3. **Invalid Requests**: FastAPI automatically validates and returns 422 for invalid schemas
4. **Google Cloud Errors**: Let them propagate as 500 errors (no retry logic for hackathon)

### Frontend Error Handling

1. **Network Errors**: Show "Unable to connect to server" message
2. **API Errors**: Display error message from backend response
3. **Empty Results**: Show "No regulations found" message
4. **Loading States**: Display spinner while waiting for API response

## Testing Strategy

### Manual Testing Approach (Hackathon-Friendly)

1. **Backend Testing**:
   - Start FastAPI server: `python backend/api_server.py`
   - Test with curl or Postman
   - Verify RAG system returns results
   - Check response format matches frontend expectations

2. **Frontend Testing**:
   - Start frontend dev server
   - Click through risk categories
   - Verify regulations load from API
   - Check overlaps and contradictions display correctly
   - Test error scenarios (stop backend, check error messages)

3. **Integration Testing**:
   - Load a subcategory with known regulations (e.g., Credit Risk)
   - Verify similarity scores are reasonable (> 0.75)
   - Check that overlaps make sense
   - Validate contradiction severity levels

### Key Test Cases

1. **Happy Path**: Select "Credit Assessment & Underwriting Standards" → See real CRR/CRD regulations
2. **LLM Analysis**: Click "Analyze" → See overlaps and contradictions
3. **Empty Results**: Search obscure subcategory → See "No regulations found"
4. **Error Handling**: Stop backend → See error message in frontend

## Deployment Considerations

### Development Setup

1. **Backend**: Run on `http://localhost:8000`
2. **Frontend**: Run on `http://localhost:5173` (Vite default)
3. **CORS**: Configure backend to allow `http://localhost:5173`

### Environment Variables

Backend needs:
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to GCP service account key
- `GCP_PROJECT_ID` - Google Cloud project ID (428461461446)
- `GCP_LOCATION` - Region (europe-west1)

Frontend needs:
- `VITE_API_URL` - Backend URL (http://localhost:8000)

### File Structure

```
project/
├── backend/
│   ├── api_server.py          # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── ragApi.ts     # API client
│   │   ├── components/       # React components (modify to use API)
│   │   └── data/
│   │       └── mockData.ts   # Keep interfaces, remove mock data
│   └── .env                  # Frontend env vars
├── rag_search.py             # Existing RAG system
└── metadata_store_production.pkl  # Existing metadata
```

## Performance Considerations

### Expected Latencies

- **Regulation Search** (no LLM): ~500ms - 1.5s
- **With LLM Analysis**: ~3-8s (depends on Gemini response time)
- **Frontend Rendering**: <100ms

### Optimization Strategies (If Time Permits)

1. **Caching**: Cache RAG results for identical queries (not implemented for hackathon)
2. **Parallel Requests**: Frontend could request regulations and analysis simultaneously
3. **Progressive Loading**: Show regulations first, then load overlaps/contradictions
4. **Reduced top_k**: Use smaller top_k values (5-10) for faster responses

## Design Decisions and Rationale

### 1. FastAPI vs Flask
**Decision**: Use FastAPI
**Rationale**: Built-in Pydantic validation, automatic OpenAPI docs, async support, modern Python

### 2. Separate Backend vs Direct Frontend-to-GCP
**Decision**: Use backend API layer
**Rationale**: 
- GCP credentials shouldn't be in frontend
- Backend can transform RAG output to match frontend interfaces
- Easier to add caching/rate limiting later

### 3. Parse LLM Text vs Structured Output
**Decision**: Parse structured LLM text sections
**Rationale**: 
- Existing RAG system returns text with clear sections (CONTRADICTIONS, OVERLAPS, etc.)
- Simple string splitting on section headers
- Faster than modifying RAG to use JSON output
- Sufficient reliability for hackathon demo

### 4. Keep Mock Data Interfaces
**Decision**: Reuse existing TypeScript interfaces
**Rationale**:
- Frontend components already work with these interfaces
- Backend transforms RAG data to match existing format
- Minimizes frontend changes

### 5. No Authentication
**Decision**: Skip auth for hackathon
**Rationale**: 
- Running locally only
- Saves development time
- Can add later if needed
