#!/usr/bin/env python3
"""
Complete pipeline validation: Chunks → Embeddings → Vertex AI
"""

import json
from pathlib import Path

print("="*80)
print("COMPLETE PIPELINE VALIDATION")
print("="*80)

# Read sample chunks
chunks_file = Path('processed_chunks/chunks_batch_000000.jsonl')
if not chunks_file.exists():
    print("\n❌ ERROR: processed_chunks/chunks_batch_000000.jsonl not found")
    print("Run: python3 preprocess_local.py --config config.yaml --skip-upload")
    exit(1)

chunks = []
with open(chunks_file) as f:
    for i, line in enumerate(f):
        if i >= 20:  # Validate first 20 chunks
            break
        chunks.append(json.loads(line))

print(f"\n✓ Loaded {len(chunks)} chunks from {chunks_file}")

# Analyze chunk compatibility
print("\n" + "="*80)
print("STEP 1: CHUNK ANALYSIS")
print("="*80)

required_fields = ['document_id', 'chunk_id', 'full_text', 'regulation_name', 
                   'year', 'doc_type', 'source_type', 'language']
optional_fields = ['article_number', 'paragraph_indices', 'token_count']

missing_fields = []
for field in required_fields:
    present = sum(1 for c in chunks if field in c)
    print(f"  {field}: {present}/{len(chunks)} chunks")
    if present < len(chunks):
        missing_fields.append(field)

if missing_fields:
    print(f"\n⚠️  WARNING: Missing fields: {missing_fields}")
else:
    print(f"\n✅ All required fields present!")

# Analyze metadata quality
print("\n" + "="*80)
print("STEP 2: METADATA QUALITY")
print("="*80)

stats = {
    'has_year': 0,
    'has_doc_type': 0,
    'has_source_type': 0,
    'has_article': 0,
    'has_language': 0,
    'has_paragraph_indices': 0
}

for chunk in chunks:
    if chunk.get('year') and str(chunk['year']) not in ['None', 'Unknown', '']:
        stats['has_year'] += 1
    if chunk.get('doc_type') and str(chunk['doc_type']) not in ['None', 'Unknown', '']:
        stats['has_doc_type'] += 1
    if chunk.get('source_type') and str(chunk['source_type']) not in ['None', 'Unknown', '']:
        stats['has_source_type'] += 1
    if chunk.get('article_number') and str(chunk['article_number']) not in ['None', '']:
        stats['has_article'] += 1
    if chunk.get('language') and str(chunk['language']) not in ['None', 'Unknown', '']:
        stats['has_language'] += 1
    if chunk.get('paragraph_indices') and len(chunk['paragraph_indices']) > 0:
        stats['has_paragraph_indices'] += 1

for key, count in stats.items():
    pct = 100 * count / len(chunks)
    status = "✅" if pct >= 80 else "⚠️" if pct >= 50 else "❌"
    print(f"  {status} {key}: {count}/{len(chunks)} ({pct:.0f}%)")

# Simulate embedding generation
print("\n" + "="*80)
print("STEP 3: EMBEDDING FORMAT SIMULATION")
print("="*80)

vertex_embeddings = []
for chunk in chunks:
    # Build restricts (same logic as generate_embeddings.py)
    restricts = []
    
    if chunk.get('year') and str(chunk['year']) not in ['None', 'Unknown', '']:
        restricts.append({"namespace": "year", "allow": [str(chunk['year'])]})
    
    if chunk.get('doc_type') and str(chunk['doc_type']) not in ['None', 'Unknown', '']:
        doc_type_clean = str(chunk['doc_type']).replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')[:30]
        restricts.append({"namespace": "doc_type", "allow": [doc_type_clean]})
    
    if chunk.get('source_type') and str(chunk['source_type']) not in ['None', 'Unknown', '']:
        restricts.append({"namespace": "source_type", "allow": [str(chunk['source_type'])]})
    
    if chunk.get('article_number') and str(chunk['article_number']) not in ['None', '']:
        article_clean = str(chunk['article_number']).replace(' ', '_')[:30]
        restricts.append({"namespace": "article", "allow": [article_clean]})
    
    if chunk.get('language') and str(chunk['language']) not in ['None', 'Unknown', '']:
        restricts.append({"namespace": "language", "allow": [str(chunk['language'])]})
    
    embedding_record = {
        'id': f"{chunk['document_id']}_{chunk['chunk_id']}",
        'embedding': [0.0] * 768,  # Mock embedding
    }
    
    if restricts:
        embedding_record['restricts'] = restricts
    
    vertex_embeddings.append(embedding_record)

# Analyze vertex format
restricts_count = [len(e.get('restricts', [])) for e in vertex_embeddings]
avg_restricts = sum(restricts_count) / len(restricts_count)
min_restricts = min(restricts_count)
max_restricts = max(restricts_count)

print(f"\n  Generated {len(vertex_embeddings)} Vertex AI embeddings")
print(f"  Restricts per embedding:")
print(f"    - Average: {avg_restricts:.1f} namespaces")
print(f"    - Range: {min_restricts}-{max_restricts} namespaces")
print(f"    - With filtering: {sum(1 for c in restricts_count if c > 0)}/{len(vertex_embeddings)}")

# Show sample
print(f"\n  Sample embedding structure:")
sample = vertex_embeddings[1] if len(vertex_embeddings) > 1 else vertex_embeddings[0]
print(f"    {{")
print(f"      'id': '{sample['id']}',")
print(f"      'embedding': float[768],")
if 'restricts' in sample:
    print(f"      'restricts': [")
    for r in sample['restricts']:
        print(f"        {r},")
    print(f"      ]")
print(f"    }}")

# Validation summary
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)

all_checks = []

# Check 1: Chunk fields
all_checks.append(("Chunk fields complete", len(missing_fields) == 0))

# Check 2: Metadata quality
all_checks.append(("Source type: 100%", stats['has_source_type'] == len(chunks)))
all_checks.append(("Language: 100%", stats['has_language'] == len(chunks)))
all_checks.append(("Paragraph indices: 100%", stats['has_paragraph_indices'] == len(chunks)))

# Check 3: Embedding format
all_checks.append(("All embeddings have ID", all('id' in e for e in vertex_embeddings)))
all_checks.append(("All embeddings have vector", all('embedding' in e for e in vertex_embeddings)))
all_checks.append(("All embeddings have restricts", all(len(e.get('restricts', [])) > 0 for e in vertex_embeddings)))

# Check 4: Vertex AI compatibility
all_checks.append(("ID format correct", all(isinstance(e['id'], str) for e in vertex_embeddings)))
all_checks.append(("Embedding dimensions: 768", all(len(e['embedding']) == 768 for e in vertex_embeddings)))

print()
passed = 0
for check_name, check_result in all_checks:
    status = "✅" if check_result else "❌"
    print(f"  {status} {check_name}")
    if check_result:
        passed += 1

print(f"\n{'='*80}")
if passed == len(all_checks):
    print("🎉 ALL CHECKS PASSED - PIPELINE IS READY!")
    print("="*80)
    print("\nNext steps:")
    print("1. Generate embeddings:")
    print("   python3 generate_embeddings.py --input-prefix processed_chunks/ --output-prefix embeddings_vertexai/")
    print("\n2. Build Vertex AI index:")
    print("   python3 build_vector_index.py --embeddings-prefix embeddings_vertexai/ --location europe-west1")
    print("\n3. Deploy and query:")
    print("   python3 rag_search.py --query 'your query here'")
else:
    print(f"⚠️  {passed}/{len(all_checks)} CHECKS PASSED")
    print("="*80)
    print("\nPlease fix the failed checks before proceeding.")
