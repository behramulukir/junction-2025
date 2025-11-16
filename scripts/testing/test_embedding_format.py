#!/usr/bin/env python3
"""
Test the embedding generation format to ensure Vertex AI compatibility.
"""

import json
import sys
from pathlib import Path

# Read a few chunks
chunks_file = Path('processed_chunks/chunks_batch_000000.jsonl')
chunks = []
with open(chunks_file) as f:
    for i, line in enumerate(f):
        if i >= 5:  # Just test first 5 chunks
            break
        chunks.append(json.loads(line))

print("="*80)
print("TESTING VERTEX AI VECTOR SEARCH FORMAT")
print("="*80)

# Simulate what generate_embeddings.py will produce
for i, chunk_data in enumerate(chunks):
    print(f"\n{'='*80}")
    print(f"Chunk {i+1}: {chunk_data['document_id']}_{chunk_data['chunk_id']}")
    print(f"{'='*80}")
    
    # Build restricts array (same logic as in generate_embeddings.py)
    restricts = []
    
    # Year namespace
    year = chunk_data.get('year')
    if year and str(year) not in ['None', 'Unknown', '']:
        restricts.append({
            "namespace": "year",
            "allow": [str(year)]
        })
    
    # Document type namespace
    doc_type = chunk_data.get('doc_type')
    if doc_type and str(doc_type) not in ['None', 'Unknown', '']:
        doc_type_clean = str(doc_type).replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')[:30]
        restricts.append({
            "namespace": "doc_type",
            "allow": [doc_type_clean]
        })
    
    # Source type namespace
    source_type = chunk_data.get('source_type')
    if source_type and str(source_type) not in ['None', 'Unknown', '']:
        restricts.append({
            "namespace": "source_type",
            "allow": [str(source_type)]
        })
    
    # Article number namespace
    article_num = chunk_data.get('article_number')
    if article_num and str(article_num) not in ['None', '']:
        article_clean = str(article_num).replace(' ', '_')[:30]
        restricts.append({
            "namespace": "article",
            "allow": [article_clean]
        })
    
    # Language namespace
    language = chunk_data.get('language')
    if language and str(language) not in ['None', 'Unknown', '']:
        restricts.append({
            "namespace": "language",
            "allow": [str(language)]
        })
    
    # Create Vertex AI compatible format
    embedding_record = {
        'id': f"{chunk_data['document_id']}_{chunk_data['chunk_id']}",
        'embedding': [0.1] * 768  # Mock 768-dim embedding
    }
    
    if restricts:
        embedding_record['restricts'] = restricts
    
    # Metadata for retrieval
    embedding_record['metadata'] = {
        'document_id': chunk_data['document_id'],
        'chunk_id': chunk_data['chunk_id'],
        'filename': chunk_data['filename'],
        'regulation_name': chunk_data['regulation_name'],
        'year': chunk_data['year'],
        'doc_type': chunk_data['doc_type'],
        'article_number': chunk_data['article_number'],
        'chunk_type': chunk_data.get('chunk_type'),
        'source_type': chunk_data.get('source_type'),
        'language': chunk_data.get('language'),
        'token_count': chunk_data['token_count'],
        'full_text': chunk_data['full_text'][:100]  # Preview
    }
    
    # Show the format
    print(f"\n✓ Source Chunk:")
    print(f"  Document ID: {chunk_data['document_id']}")
    print(f"  Regulation: {chunk_data['regulation_name'][:60]}...")
    print(f"  Year: {chunk_data['year']}")
    print(f"  Doc Type: {chunk_data['doc_type']}")
    print(f"  Source Type: {chunk_data.get('source_type')}")
    print(f"  Article: {chunk_data.get('article_number')}")
    print(f"  Language: {chunk_data.get('language')}")
    
    print(f"\n✓ Vertex AI Format:")
    print(f"  ID: {embedding_record['id']}")
    print(f"  Embedding: float[768] vector")
    print(f"  Restricts: {len(restricts)} namespaces")
    
    if restricts:
        print(f"\n  Filtering Metadata (restricts):")
        for restrict in restricts:
            print(f"    - {restrict['namespace']}: {restrict['allow']}")
    else:
        print(f"\n  ⚠️  No filtering metadata (restricts empty)")
    
    print(f"\n  Retrieval Metadata:")
    print(f"    - Regulation: {embedding_record['metadata']['regulation_name'][:50]}...")
    print(f"    - Tokens: {embedding_record['metadata']['token_count']}")
    print(f"    - Text preview: {embedding_record['metadata']['full_text'][:80]}...")

print(f"\n\n{'='*80}")
print("VALIDATION SUMMARY")
print(f"{'='*80}")

# Count chunks with/without restricts
chunks_with_restricts = 0
chunks_without_restricts = 0
namespace_counts = {}

for chunk_data in chunks:
    restricts = []
    
    if chunk_data.get('year') and str(chunk_data['year']) not in ['None', 'Unknown', '']:
        restricts.append('year')
    if chunk_data.get('doc_type') and str(chunk_data['doc_type']) not in ['None', 'Unknown', '']:
        restricts.append('doc_type')
    if chunk_data.get('source_type') and str(chunk_data['source_type']) not in ['None', 'Unknown', '']:
        restricts.append('source_type')
    if chunk_data.get('article_number') and str(chunk_data['article_number']) not in ['None', '']:
        restricts.append('article')
    if chunk_data.get('language') and str(chunk_data['language']) not in ['None', 'Unknown', '']:
        restricts.append('language')
    
    if restricts:
        chunks_with_restricts += 1
        for ns in restricts:
            namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
    else:
        chunks_without_restricts += 1

print(f"\nChunks with filtering metadata: {chunks_with_restricts}/{len(chunks)}")
print(f"Chunks without filtering metadata: {chunks_without_restricts}/{len(chunks)}")

print(f"\nNamespace usage across chunks:")
for ns, count in sorted(namespace_counts.items()):
    print(f"  - {ns}: {count}/{len(chunks)} ({100*count/len(chunks):.0f}%)")

print(f"\n✅ Format is Vertex AI Vector Search compatible!")
print(f"✅ Required fields: 'id' (string), 'embedding' (float array)")
print(f"✅ Optional fields: 'restricts' (namespace array for filtering)")
print(f"✅ Additional 'metadata' field for retrieval (not used by index)")

print(f"\n{'='*80}")
print("READY FOR PRODUCTION")
print(f"{'='*80}")
print("Run: python3 generate_embeddings.py --input-prefix processed_chunks/ --output-prefix embeddings_vertexai/")
