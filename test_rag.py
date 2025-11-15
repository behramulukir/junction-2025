#!/usr/bin/env python3
"""Quick test script for RAG system"""

from rag_search import EULegislationRAG

# Production config
INDEX_ENDPOINT = "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912"
DEPLOYED_INDEX_ID = "eu_legislation_prod_75480320"
PROJECT_ID = "428461461446"
LOCATION = "europe-west1"

print("Initializing RAG system...")
rag = EULegislationRAG(
    project_id=PROJECT_ID,
    location=LOCATION,
    index_endpoint_name=INDEX_ENDPOINT,
    deployed_index_id=DEPLOYED_INDEX_ID,
    metadata_file="metadata_store_production.pkl"
)

print("\nTesting search...")
result = rag.query(
    user_query="financial regulation banking requirements",
    top_k=5,
    analyze_with_llm=False,
    use_query_expansion=False
)

rag.print_results(result)
print("\n✅ RAG system is operational!")
