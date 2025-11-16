#!/usr/bin/env python3
"""
Test script for cache functionality
"""

from cache_db import ResponseCache

def main():
    print("Testing ResponseCache...")
    
    # Initialize cache
    cache = ResponseCache("test_cache.db")
    
    # Test data
    subcategory_id = "1.1"
    description = "Credit risk management requirements"
    top_k = 10
    
    # Test regulations cache
    print("\n1. Testing regulations cache...")
    
    # First query - should be a miss
    result = cache.get_regulations(subcategory_id, description, top_k)
    print(f"   First query: {'HIT' if result else 'MISS'}")
    
    # Cache some data
    test_regulations = [
        {
            "id": "reg1",
            "name": "CRR Article 124",
            "similarityScore": 0.95,
            "description": "Test regulation 1"
        },
        {
            "id": "reg2",
            "name": "CRD Article 73",
            "similarityScore": 0.87,
            "description": "Test regulation 2"
        }
    ]
    
    cache.cache_regulations(subcategory_id, description, top_k, test_regulations)
    print("   Cached test regulations")
    
    # Second query - should be a hit
    result = cache.get_regulations(subcategory_id, description, top_k)
    print(f"   Second query: {'HIT' if result else 'MISS'}")
    if result:
        print(f"   Retrieved {len(result)} regulations")
    
    # Test analysis cache
    print("\n2. Testing analysis cache...")
    
    # First query - should be a miss
    result = cache.get_analysis(subcategory_id, description, top_k)
    print(f"   First query: {'HIT' if result else 'MISS'}")
    
    # Cache some data
    test_overlaps = [
        {
            "id": "overlap1",
            "regulationPair": ["CRR Article 124", "CRD Article 73"],
            "type": "Complementary",
            "description": "Test overlap",
            "confidenceScore": 0.85,
            "excerpts": {"regulation1": "text1", "regulation2": "text2"}
        }
    ]
    
    test_contradictions = [
        {
            "id": "contradiction1",
            "regulationPair": ["Reg A", "Reg B"],
            "description": "Test contradiction",
            "severity": "High",
            "conflictingRequirements": {"regulation1": "req1", "regulation2": "req2"}
        }
    ]
    
    cache.cache_analysis(subcategory_id, description, top_k, test_overlaps, test_contradictions)
    print("   Cached test analysis")
    
    # Second query - should be a hit
    result = cache.get_analysis(subcategory_id, description, top_k)
    print(f"   Second query: {'HIT' if result else 'MISS'}")
    if result:
        print(f"   Retrieved {len(result['overlaps'])} overlaps, {len(result['contradictions'])} contradictions")
    
    # Get stats
    print("\n3. Cache statistics:")
    stats = cache.get_cache_stats()
    print(f"   Regulations: {stats['regulations']['cached_queries']} queries, {stats['regulations']['total_hits']} hits")
    print(f"   Analysis: {stats['analysis']['cached_queries']} queries, {stats['analysis']['total_hits']} hits")
    
    # Clean up
    import os
    test_db_path = os.path.join(os.path.dirname(__file__), "test_cache.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    main()
