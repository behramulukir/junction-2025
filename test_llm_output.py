#!/usr/bin/env python3
"""Quick test to see LLM analysis output format"""

from rag_search import EULegislationRAG

# Initialize RAG
rag = EULegislationRAG(
    project_id="428461461446",
    location="europe-west1",
    index_endpoint_name="projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912",
    deployed_index_id="eu_legislation_prod_75480320"
)

# Test query with LLM analysis
print("Testing LLM analysis output format...")
print("=" * 80)

result = rag.query(
    user_query="credit risk assessment and underwriting requirements",
    top_k=20,
    analyze_with_llm=True,
    focus_cross_regulation=True,
    use_query_expansion=False
)

llm_analysis = result.get('llm_analysis', '')

if llm_analysis:
    print("LLM ANALYSIS OUTPUT:")
    print("=" * 80)
    print(llm_analysis)
    print("=" * 80)
    print(f"\nTotal length: {len(llm_analysis)} characters")
    
    # Check for section headers
    sections = ['SUMMARY', 'KEY FINDINGS', 'CONTRADICTIONS', 'OVERLAPS', 'RECOMMENDATIONS']
    print("\nSection headers found:")
    for section in sections:
        if section in llm_analysis:
            print(f"  ✓ {section}")
        else:
            print(f"  ✗ {section}")
else:
    print("No LLM analysis returned")
