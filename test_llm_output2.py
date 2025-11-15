#!/usr/bin/env python3
"""Test with a different query to confirm LLM output pattern"""

from rag_search import EULegislationRAG

rag = EULegislationRAG(
    project_id="428461461446",
    location="europe-west1",
    index_endpoint_name="projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912",
    deployed_index_id="eu_legislation_prod_75480320"
)

print("Testing with liquidity requirements query...")
print("=" * 80)

result = rag.query(
    user_query="liquidity coverage ratio and funding requirements",
    top_k=15,
    analyze_with_llm=True,
    focus_cross_regulation=True,
    use_query_expansion=False
)

llm_analysis = result.get('llm_analysis', '')

if llm_analysis:
    # Check for section headers
    sections = ['SUMMARY', 'KEY FINDINGS', 'CONTRADICTIONS', 'OVERLAPS', 'RECOMMENDATIONS']
    print("\nSection headers found:")
    for section in sections:
        count = llm_analysis.count(section)
        if count > 0:
            print(f"  ✓ {section} (appears {count} time(s))")
        else:
            print(f"  ✗ {section}")
    
    # Show first 1500 chars
    print("\nFirst 1500 characters of output:")
    print("=" * 80)
    print(llm_analysis[:1500])
    print("=" * 80)
else:
    print("No LLM analysis returned")
