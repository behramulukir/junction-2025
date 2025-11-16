#!/usr/bin/env python3
"""
Test RAG query directly to see what similarity scores we get
"""

from rag_search import EULegislationRAG

# Initialize RAG system
print("Initializing RAG system...")
rag = EULegislationRAG(
    project_id="428461461446",
    location="europe-west1",
    index_endpoint_name="projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912",
    deployed_index_id="eu_legislation_prod_75480320",
    metadata_file="metadata_store_production.pkl"
)
print("RAG system initialized\n")

# Test queries
test_queries = [
    "Credit spread risk in the trading book",
    "banking capital requirements",
    "MiFID II financial markets regulation",
    "fishing vessel regulations",
]

for query in test_queries:
    print("=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)
    
    result = rag.query(
        user_query=query,
        top_k=5,
        analyze_with_llm=False,
        use_query_expansion=False
    )
    
    print(f"\nFound {result['num_results']} results:\n")
    
    for i, chunk in enumerate(result['top_chunks'], 1):
        metadata = chunk['metadata']
        print(f"{i}. Score: {chunk['score']:.4f}")
        print(f"   Regulation: {metadata.get('regulation_name', 'Unknown')}")
        print(f"   Year: {metadata.get('year', 'N/A')} | Type: {metadata.get('doc_type', 'Unknown')}")
        print(f"   Article: {metadata.get('article_number', 'N/A')}")
        print(f"   Text preview: {metadata.get('full_text', '')[:150]}...")
        print()
    
    print()
