# Implementation Plan

- [x] 1. Create Backend API Server





  - Create `backend/api_server.py` with FastAPI application
  - Implement CORS middleware to allow frontend origin
  - Import and initialize EULegislationRAG from existing `rag_search.py`
  - _Requirements: 4.2, 4.5_

- [x] 1.1 Implement /api/regulations endpoint


  - Create Pydantic request model with subcategory_id, subcategory_description, and top_k fields
  - Call `rag.query()` with subcategory description and analyze_with_llm=False
  - Transform RAG results to match frontend Regulation interface format
  - Return JSON response with regulations array
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 1.2 Implement /api/analyze endpoint


  - Create Pydantic request model with subcategory_id, subcategory_description, and top_k fields
  - Call `rag.query()` with analyze_with_llm=True and focus_cross_regulation=True
  - Parse LLM analysis text by splitting on section headers (CONTRADICTIONS, OVERLAPS)
  - Extract regulation pairs, descriptions, severity levels, and excerpts
  - Return JSON response with overlaps and contradictions arrays
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4_

- [x] 1.3 Add error handling to API endpoints


  - Wrap rag.query() calls in try-except blocks
  - Return 500 status with error message on exceptions
  - Return 200 with empty arrays when no results found
  - _Requirements: 4.1, 4.3_

- [x] 1.4 Create backend requirements.txt and setup


  - List FastAPI, uvicorn, pydantic dependencies
  - Include existing google-cloud dependencies from rag_search.py
  - Add python-dotenv for environment variables
  - _Requirements: 4.4_

- [x] 2. Create Frontend API Client





  - Create `frontend/src/api/ragApi.ts` file
  - Implement fetchRegulations() function that calls POST /api/regulations
  - Implement fetchAnalysis() function that calls POST /api/analyze
  - Add error handling for network failures and API errors
  - Use environment variable for API base URL
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 4.4_

- [x] 3. Integrate API into Frontend Components





  - Identify which component displays subcategory details
  - Replace mock data import with API calls
  - Add loading state while fetching regulations
  - Add error state display for API failures
  - Update component to call fetchRegulations() when subcategory selected
  - Update component to call fetchAnalysis() when user requests overlap/contradiction analysis
  - _Requirements: 1.3, 2.5, 3.4, 4.4_

- [x] 4. Configure Environment Variables





  - Create `backend/.env` with GOOGLE_APPLICATION_CREDENTIALS, GCP_PROJECT_ID, GCP_LOCATION
  - Create `frontend/.env` with VITE_API_URL=http://localhost:8000
  - Update .gitignore to exclude .env files
  - _Requirements: 4.4_

- [ ] 5. Test Integration End-to-End
  - Start backend server on port 8000
  - Start frontend dev server on port 5173
  - Click through risk categories in frontend
  - Verify regulations load from API with real data
  - Test analyze functionality for overlaps and contradictions
  - Verify error handling when backend is stopped
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 4.1, 4.3_
