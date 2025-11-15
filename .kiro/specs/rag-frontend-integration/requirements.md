# Requirements Document

## Introduction

This feature integrates the existing frontend application with the vector database RAG system to replace mock regulation data with real EU legislation search results. The system will query the vector database for relevant regulations based on risk subcategories and use LLM analysis to identify genuine overlaps and contradictions between regulations.

## Glossary

- **RAG System**: Retrieval-Augmented Generation system that combines vector similarity search with LLM analysis for EU legislation
- **Vector Database**: Google Cloud Vertex AI Matching Engine containing 225,168 EU legislation chunks with embeddings
- **Frontend Application**: React/TypeScript web application displaying risk categories and regulations
- **Backend API**: FastAPI service that interfaces between the frontend and RAG system
- **Risk Subcategory**: Specific area within a risk category (e.g., "Credit Assessment & Underwriting Standards")
- **Regulation Chunk**: Individual segment of EU legislation with metadata (regulation name, article, year, full text)
- **Overlap**: Situation where multiple regulations address similar requirements (Duplicate, Complementary, or Conflicting types)
- **Contradiction**: Conflict between regulations with different requirements for the same scenario
- **LLM Analysis**: Gemini-powered analysis that identifies overlaps and contradictions from regulation text

## Requirements

### Requirement 1

**User Story:** As a compliance officer, I want to see real EU regulations relevant to each risk subcategory, so that I can understand actual regulatory requirements instead of mock data

#### Acceptance Criteria

1. WHEN the Frontend Application loads a risk subcategory, THE Backend API SHALL query the RAG System using the subcategory description as the search query
2. THE Backend API SHALL return between 5 and 20 regulation chunks with similarity scores above 0.75
3. THE Frontend Application SHALL display regulation names, article numbers, similarity scores, and descriptions from the RAG System results
4. WHERE a risk subcategory has associated keywords, THE Backend API SHALL include those keywords in the search query to improve relevance
5. THE Backend API SHALL complete regulation searches within 2 seconds for queries without LLM analysis

### Requirement 2

**User Story:** As a compliance officer, I want to identify genuine overlaps between regulations, so that I can understand where multiple regulations address the same requirements

#### Acceptance Criteria

1. WHEN the Backend API receives a request to analyze overlaps for a subcategory, THE Backend API SHALL query the RAG System with LLM analysis enabled
2. THE RAG System SHALL return regulation chunks with top_k set to 30 to provide sufficient context for overlap detection
3. THE LLM Analysis SHALL identify overlaps and classify each as Duplicate, Complementary, or Conflicting type
4. THE Backend API SHALL extract overlap information from the LLM Analysis and format it according to the Frontend Application's Overlap interface
5. THE Frontend Application SHALL display overlap pairs with regulation names, type classification, description, confidence score, and text excerpts from both regulations

### Requirement 3

**User Story:** As a compliance officer, I want to discover contradictions between regulations, so that I can identify conflicting requirements that need resolution

#### Acceptance Criteria

1. WHEN the Backend API receives a request to analyze contradictions for a subcategory, THE Backend API SHALL enable focus_cross_regulation parameter in the RAG System query
2. THE LLM Analysis SHALL identify contradictions between different regulations with severity levels (High, Medium, or Low)
3. THE Backend API SHALL extract contradiction information including regulation pairs, description, severity, and conflicting requirement texts
4. THE Frontend Application SHALL display contradictions with clear indication of severity and specific conflicting requirements from each regulation
5. IF no contradictions are found, THE Frontend Application SHALL display a message indicating no conflicts were detected

### Requirement 4

**User Story:** As a developer, I want the backend API to work with the frontend, so that I can demonstrate the integration quickly

#### Acceptance Criteria

1. THE Backend API SHALL expose REST endpoints that accept subcategory descriptions and return regulation data
2. THE Backend API SHALL implement CORS configuration to allow requests from the Frontend Application origin
3. IF the RAG System query fails, THE Backend API SHALL return an error response with HTTP status code 500
4. THE Frontend Application SHALL replace mock data imports with API calls to the Backend API
5. THE Backend API SHALL run on a different port than the Frontend Application to avoid conflicts
