#!/usr/bin/env python3
"""
FastAPI backend server for RAG-Frontend integration
Provides REST endpoints for querying EU legislation and analyzing overlaps/contradictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
import sys
import os
import re

# Add parent directory to path to import rag_search
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_search import EULegislationRAG
from cache_db import ResponseCache

# Configuration
PROJECT_ID = "428461461446"
LOCATION = "europe-west1"
INDEX_ENDPOINT_NAME = "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912"
DEPLOYED_INDEX_ID = "eu_legislation_prod_75480320"

# Try multiple paths for metadata file (local dev vs production)
METADATA_PATHS = [
    os.getenv("METADATA_FILE", "metadata_store_production.pkl"),  # Same directory (production)
    "metadata_store_production.pkl",  # Same directory
    "../metadata_store_production.pkl",  # Parent directory (if running from backend/)
    os.path.join(os.path.dirname(__file__), "metadata_store_production.pkl"),  # Relative to this file
]

METADATA_FILE = None
for path in METADATA_PATHS:
    if os.path.exists(path):
        METADATA_FILE = path
        print(f"Found metadata file at: {path}")
        break

if not METADATA_FILE:
    print("WARNING: metadata_store_production.pkl not found in any expected location!")
    print(f"Searched paths: {METADATA_PATHS}")
    METADATA_FILE = "metadata_store_production.pkl"  # Use default, will fail gracefully

# Initialize FastAPI app
app = FastAPI(
    title="EU Legislation RAG API",
    description="Backend API for querying EU legislation using RAG system",
    version="1.0.0"
)

# Configure CORS - allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize RAG system
print("Initializing RAG system...")
rag = EULegislationRAG(
    project_id=PROJECT_ID,
    location=LOCATION,
    index_endpoint_name=INDEX_ENDPOINT_NAME,
    deployed_index_id=DEPLOYED_INDEX_ID,
    metadata_file=METADATA_FILE
)
print("RAG system initialized successfully")

# Initialize cache
print("Initializing response cache...")
cache = ResponseCache()
print("Cache initialized successfully")


# Pydantic Models
class RegulationRequest(BaseModel):
    subcategory_id: str = Field(..., description="Subcategory ID (e.g., '1.1')")
    subcategory_description: str = Field(..., description="Description of the subcategory to search")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=50)


class RegulationMetadata(BaseModel):
    article_number: Optional[str] = None
    year: Optional[int] = None
    full_text: Optional[str] = None
    regulation_name: Optional[str] = None
    doc_type: Optional[str] = None


class RegulationResponse(BaseModel):
    id: str
    name: str
    similarityScore: float
    description: str
    metadata: Optional[Dict] = None


class AnalysisRequest(BaseModel):
    subcategory_id: str = Field(..., description="Subcategory ID (e.g., '1.1')")
    subcategory_description: str = Field(..., description="Description of the subcategory to analyze")
    top_k: int = Field(30, description="Number of results to retrieve for analysis", ge=10, le=50)


class OverlapResponse(BaseModel):
    id: str
    regulationPair: Tuple[str, str]
    type: str  # Duplicate | Complementary | Conflicting
    description: str
    confidenceScore: float
    excerpts: Dict[str, str]


class ContradictionResponse(BaseModel):
    id: str
    regulationPair: Tuple[str, str]
    description: str
    severity: str  # High | Medium | Low
    conflictingRequirements: Dict[str, str]


class AnalysisResult(BaseModel):
    overlaps: List[OverlapResponse]
    contradictions: List[ContradictionResponse]
    full_analysis: Optional[str] = None


# Helper Functions
def format_regulation_name(metadata: Dict) -> str:
    """Format regulation name from metadata."""
    parts = []
    if metadata.get('regulation_name'):
        parts.append(metadata['regulation_name'])
    if metadata.get('article_number'):
        parts.append(f"Article {metadata['article_number']}")
    
    return " - ".join(parts) if parts else metadata.get('id', 'Unknown Regulation')


def format_description(metadata: Dict) -> str:
    """Format description from full text."""
    full_text = metadata.get('full_text', '')
    # Return full text - truncation will be handled by frontend
    return full_text


def transform_rag_to_regulations(rag_result: Dict, min_results: int = 5) -> List[RegulationResponse]:
    """Transform RAG results to frontend Regulation format.
    
    Args:
        rag_result: RAG query result
        min_results: Minimum number of results to return (returns all if less available)
    """
    regulations = []
    
    for chunk in rag_result.get('top_chunks', []):
        metadata = chunk.get('metadata', {})
        
        regulation = RegulationResponse(
            id=chunk.get('id', ''),
            name=format_regulation_name(metadata),
            similarityScore=round(chunk.get('score', 0.0), 2),
            description=format_description(metadata),
            metadata=metadata
        )
        regulations.append(regulation)
    
    # Always return at least min_results (or all if less available)
    return regulations



# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "EU Legislation RAG API",
        "version": "1.0.0"
    }


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = cache.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@app.delete("/api/cache")
async def clear_cache():
    """Clear all cached data."""
    try:
        cache.clear_cache()
        return {"status": "ok", "message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@app.post("/api/regulations", response_model=Dict[str, List[RegulationResponse]])
async def get_regulations(request: RegulationRequest):
    """
    Get relevant regulations for a subcategory.
    
    Args:
        request: RegulationRequest with subcategory details
        
    Returns:
        Dict with regulations array
    """
    try:
        # Check cache first
        cached_regulations = cache.get_regulations(
            request.subcategory_id,
            request.subcategory_description,
            request.top_k
        )
        
        if cached_regulations:
            print(f"Cache HIT for regulations: {request.subcategory_id}")
            return {"regulations": cached_regulations}
        
        print(f"Cache MISS for regulations: {request.subcategory_id}")
        
        # Query RAG system without LLM analysis
        result = rag.query(
            user_query=request.subcategory_description,
            top_k=request.top_k,
            analyze_with_llm=False,
            use_query_expansion=False  # Faster for simple queries
        )
        
        # Transform to frontend format
        regulations = transform_rag_to_regulations(result)
        
        # Convert to dict for caching (use model_dump instead of deprecated dict)
        regulations_dict = [reg.model_dump() for reg in regulations]
        
        # Cache the result
        cache.cache_regulations(
            request.subcategory_id,
            request.subcategory_description,
            request.top_k,
            regulations_dict
        )
        
        return {"regulations": regulations}
        
    except Exception as e:
        print(f"Error in /api/regulations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve regulations: {str(e)}"
        )



def parse_llm_analysis(llm_text: str) -> Tuple[List[OverlapResponse], List[ContradictionResponse]]:
    """
    Parse LLM analysis text to extract overlaps (contradictions are treated as overlaps).
    
    Args:
        llm_text: LLM analysis text with sections
        
    Returns:
        Tuple of (overlaps, empty list for contradictions)
    """
    overlaps = []
    contradictions = []  # Always empty now
    
    if not llm_text:
        print("No LLM text to parse")
        return overlaps, contradictions
    
    # Split into sections - only look for OVERLAPS
    VALID_SECTIONS = {'SUMMARY', 'OVERLAPS'}
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in llm_text.split('\n'):
        line_stripped = line.strip()
        
        # Check if line is a valid section header (all caps, short, matches our sections)
        line_upper = line_stripped.upper().rstrip(':')
        
        if line_upper in VALID_SECTIONS and len(line_stripped) < 50:
            # Found a valid section header
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line_upper
            current_content = []
            print(f"Found section: {line_upper}")
        else:
            current_content.append(line)
    
    # Add last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    print(f"Parsed sections: {list(sections.keys())}")
    
    # Parse OVERLAPS section (includes contradictions)
    overlaps_text = sections.get('OVERLAPS', '')
    if overlaps_text:
        overlaps = parse_overlaps(overlaps_text)
        print(f"Found {len(overlaps)} overlaps")
    else:
        print("No OVERLAPS section found")
    
    return overlaps, contradictions


def parse_overlaps(text: str) -> List[OverlapResponse]:
    """Parse overlaps from text section.
    
    Expected format:
    1. Regulation Name Article X vs Regulation Name Article Y - Description here.
    """
    overlaps = []
    
    # Check for "None identified"
    if "none identified" in text.lower().strip():
        return overlaps
    
    # Clean up text - remove bold formatting and extra keywords
    text = re.sub(r'\*\*', '', text)  # Remove ** bold markers
    text = re.sub(r'Quote:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Quote: sections
    text = re.sub(r'Explanation:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Explanation: sections
    text = re.sub(r'Severity:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Severity: sections
    text = re.sub(r'Practical Impact:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Practical Impact: sections
    
    # Join lines that don't start with a number - this handles multi-line items
    lines = text.split('\n')
    joined_lines = []
    current_item = ""
    
    for line in lines:
        line = line.strip()
        # Check if line starts with a number followed by period (new item)
        if re.match(r'^\d+\.\s+', line):
            if current_item:
                joined_lines.append(current_item)
            current_item = line
        else:
            # Continuation of previous item
            if current_item:
                current_item += " " + line
            elif line:  # First line might not start with number
                current_item = line
    
    # Add last item
    if current_item:
        joined_lines.append(current_item)
    
    text = '\n'.join(joined_lines)
    
    print(f"\nParsing overlaps section ({len(text)} chars)")
    print(f"After joining multi-line items (FULL TEXT):\n{text}\n")
    print("="*80)
    
    # Split by numbered items (1., 2., etc.) at start of line
    items = re.split(r'\n\s*(\d+)\.\s+', text)
    print(f"Split into {len(items)} parts")
    for idx, part in enumerate(items):
        print(f"  Part {idx}: {part[:100]}")
    
    # Items come in pairs: [number, content, number, content, ...]
    for i in range(1, len(items), 2):
        if i + 1 >= len(items):
            break
            
        idx = items[i]
        item = items[i + 1].strip()
        
        print(f"\n  Processing overlap #{idx}:")
        print(f"    First 200 chars: {item[:200]}")
        
        if not item or len(item) < 10:
            print(f"    ✗ Skipped: too short")
            continue
        
        try:
            # Extract regulation pair: "Reg A Article X vs Reg B Article Y"
            # Look for pattern: text vs text - description
            pair_match = re.search(r'^(.+?)\s+vs\s+(.+?)\s*[-–—]\s*(.+)$', item, re.DOTALL)
            
            if not pair_match:
                print(f"    ✗ Could not parse overlap format (no 'vs' pattern found)")
                continue
            
            reg1 = pair_match.group(1).strip()
            reg2 = pair_match.group(2).strip()
            description = pair_match.group(3).strip()
            
            # Remove trailing period and clean up
            description = description.rstrip('.').strip()
            
            overlap = OverlapResponse(
                id=f"overlap-{idx}",
                regulationPair=(reg1, reg2),
                type="Complementary",  # Default, frontend can categorize if needed
                description=description,
                confidenceScore=0.85,
                excerpts={"regulation1": "", "regulation2": ""}
            )
            overlaps.append(overlap)
            print(f"  ✓ Parsed overlap: {reg1} vs {reg2}")
            
        except Exception as e:
            print(f"  ✗ Error parsing overlap: {e}")
            print(f"    Item: {item[:150]}")
            continue
    
    return overlaps


def parse_contradictions(text: str) -> List[ContradictionResponse]:
    """Parse contradictions from text section.
    
    Expected format:
    1. Regulation Name Article X vs Regulation Name Article Y - Description here.
    """
    contradictions = []
    
    # Check for "None identified"
    if "none identified" in text.lower().strip():
        return contradictions
    
    # Clean up text - remove bold formatting and extra keywords
    text = re.sub(r'\*\*', '', text)  # Remove ** bold markers
    text = re.sub(r'Quote:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Quote: sections
    text = re.sub(r'Explanation:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Explanation: sections
    text = re.sub(r'Severity:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Severity: sections
    text = re.sub(r'Practical Impact:.*?(?=\n|$)', '', text, flags=re.IGNORECASE)  # Remove Practical Impact: sections
    
    # Split by numbered items (1., 2., etc.) at start of line
    items = re.split(r'\n\s*(\d+)\.\s+', text)
    
    # Items come in pairs: [number, content, number, content, ...]
    for i in range(1, len(items), 2):
        if i + 1 >= len(items):
            break
            
        idx = items[i]
        item = items[i + 1].strip()
        
        if not item or len(item) < 10:
            continue
        
        try:
            # Extract regulation pair: "Reg A Article X vs Reg B Article Y"
            # Look for pattern: text vs text - description
            pair_match = re.search(r'^(.+?)\s+vs\s+(.+?)\s*[-–—]\s*(.+)$', item, re.DOTALL)
            
            if not pair_match:
                print(f"  Could not parse contradiction format: {item[:100]}")
                continue
            
            reg1 = pair_match.group(1).strip()
            reg2 = pair_match.group(2).strip()
            description = pair_match.group(3).strip()
            
            # Remove trailing period and clean up
            description = description.rstrip('.').strip()
            
            contradiction = ContradictionResponse(
                id=f"contradiction-{idx}",
                regulationPair=(reg1, reg2),
                description=description,
                severity="Medium",  # Default, frontend can display differently if needed
                conflictingRequirements={"regulation1": "", "regulation2": ""}
            )
            contradictions.append(contradiction)
            print(f"  ✓ Parsed contradiction: {reg1} vs {reg2}")
            
        except Exception as e:
            print(f"  ✗ Error parsing contradiction: {e}")
            print(f"    Item: {item[:150]}")
            continue
    
    return contradictions


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_regulations(request: AnalysisRequest):
    """
    Analyze regulations for overlaps and contradictions.
    
    Args:
        request: AnalysisRequest with subcategory details
        
    Returns:
        AnalysisResult with overlaps and contradictions
    """
    try:
        # Check cache first
        cached_analysis = cache.get_analysis(
            request.subcategory_id,
            request.subcategory_description,
            request.top_k
        )
        
        if cached_analysis:
            print(f"Cache HIT for analysis: {request.subcategory_id}")
            return AnalysisResult(
                overlaps=cached_analysis['overlaps'],
                contradictions=cached_analysis['contradictions']
            )
        
        print(f"Cache MISS for analysis: {request.subcategory_id}")
        
        # Query RAG system with LLM analysis
        result = rag.query(
            user_query=request.subcategory_description,
            top_k=request.top_k,
            analyze_with_llm=True,
            focus_cross_regulation=True,
            use_query_expansion=False
        )
        
        # Parse LLM analysis
        llm_analysis = result.get('llm_analysis', '')
        raw_analysis = result.get('raw_analysis', '')
        print(f"Raw LLM Analysis (first 500 chars):\n{llm_analysis[:500]}")
        overlaps, contradictions = parse_llm_analysis(llm_analysis)
        
        # Convert to dict for caching (use model_dump instead of deprecated dict)
        overlaps_dict = [overlap.model_dump() for overlap in overlaps]
        contradictions_dict = []  # Empty since we treat everything as overlaps
        
        # Cache the result (note: not caching raw_analysis for now)
        cache.cache_analysis(
            request.subcategory_id,
            request.subcategory_description,
            request.top_k,
            overlaps_dict,
            contradictions_dict
        )
        
        return AnalysisResult(
            overlaps=overlaps,
            contradictions=[],  # Always empty
            full_analysis=raw_analysis
        )
        
    except Exception as e:
        print(f"Error in /api/analyze: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze regulations: {str(e)}"
        )




# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Verify RAG system is ready on startup."""
    try:
        print("Verifying RAG system initialization...")
        if not rag.metadata_store:
            print("WARNING: Metadata store is empty!")
        else:
            print(f"RAG system ready with {len(rag.metadata_store)} metadata entries")
    except Exception as e:
        print(f"ERROR during startup: {e}")


if __name__ == "__main__":
    import uvicorn
    
    print("Starting FastAPI server...")
    print("API will be available at: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
