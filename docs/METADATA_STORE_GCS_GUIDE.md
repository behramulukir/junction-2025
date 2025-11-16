# Metadata Store GCS Integration Guide

## Overview

The metadata store can now be built from **both local and GCS sources**, including:
- ✅ **Processed chunks** (local or GCS) - RECOMMENDED
- ⚠️ **Embeddings** (GCS only) - NOT RECOMMENDED (missing new fields)

## Data Sources in GCS Bucket

Your `bof-hackathon-data-eu` bucket contains:

```
gs://bof-hackathon-data-eu/
├── processed_chunks/           # FULL dataset source chunks (225K+ chunks)
├── test_chunks/               # TEST dataset source chunks (small subset)
├── embeddings_vertexai_json/  # FULL embeddings (274K+ entries) ⚠️ MISSING NEW FIELDS
└── test_embeddings_index/     # TEST embeddings (small subset) ⚠️ MISSING NEW FIELDS
```

## ⚠️ Critical Issue: Embeddings Missing New Metadata

**Problem:** The embeddings in GCS (`embeddings_vertexai_json/`, `test_embeddings_index/`) were generated **BEFORE** the new metadata fields were added to processed chunks.

### Missing Fields in Embeddings:
- `paragraph_indices` - Used for paragraph-level context extraction
- `chunk_type` - article/recital/section/mixed classification
- `language` - en/fi/multi language tags
- `source_type` - eu_legislation/national_law/international_standard

### Fields Present in Embeddings:
- `document_id`, `chunk_id`, `filename`
- `regulation_name`, `year`, `doc_type`
- `article_number`, `paragraph_numbers`
- `full_text`, `token_count`
- `regulation_refs`, `char_start`, `char_end`

## Recommended Approach

### For Production: Build from GCS Processed Chunks

```bash
# Build production metadata store from GCS processed chunks
python scripts/utilities/build_metadata_store.py \
  --from-chunks gs://bof-hackathon-data-eu/processed_chunks \
  --output metadata_store_production.pkl
```

**Why?** This preserves ALL 17 metadata fields including the new ones.

### For Testing: Build from Local or GCS Test Chunks

```bash
# From local test chunks
python scripts/utilities/build_metadata_store.py \
  --from-chunks processed_chunks \
  --output metadata_store_test.pkl

# From GCS test chunks
python scripts/utilities/build_metadata_store.py \
  --from-chunks gs://bof-hackathon-data-eu/test_chunks \
  --output metadata_store_test.pkl
```

### Legacy: Build from Embeddings (NOT RECOMMENDED)

```bash
# Build from embeddings (missing new fields)
python scripts/utilities/build_metadata_store.py \
  --from-embeddings gs://bof-hackathon-data-eu/embeddings_vertexai_json \
  --output metadata_store_legacy.pkl
```

⚠️ **Warning:** This will fill missing fields with defaults:
- `paragraph_indices: []` (empty - RAG paragraph extraction won't work)
- `chunk_type: "unknown"` (filtering by article/recital won't work)
- `language: "en"` (default - language filtering may be inaccurate)
- `source_type: "eu_legislation"` (default - source filtering may be inaccurate)

## Metadata Comparison

### Processed Chunks (FULL metadata)
```json
{
  "id": "125480ac-2957-11e6-b616-01aa75ed71a1_0",
  "document_id": "125480ac-2957-11e6-b616-01aa75ed71a1",
  "filename": "L_2016147EN.01003401.json",
  "regulation_name": "ANNEX II",
  "year": null,
  "doc_type": "Unknown",
  "chunk_id": 0,
  "chunk_type": "section",
  "article_number": null,
  "paragraph_numbers": [],
  "paragraph_indices": [[10,18], [19,85], ...],  // ✅ PRESENT
  "char_start": 0,
  "char_end": 1239,
  "token_count": 542,
  "regulation_refs": [],
  "language": "en",                              // ✅ PRESENT
  "source_type": "eu_legislation",               // ✅ PRESENT
  "full_text": "ANNEX II\n\n..."
}
```

### Embeddings (PARTIAL metadata)
```json
{
  "id": "125480ac-2957-11e6-b616-01aa75ed71a1_0",
  "metadata": {
    "document_id": "125480ac-2957-11e6-b616-01aa75ed71a1",
    "chunk_id": 0,
    "filename": "L_2016147EN.01003401.json",
    "regulation_name": "ANNEX II",
    "year": null,
    "doc_type": "Unknown",
    "article_number": null,
    "paragraph_numbers": [],
    // ❌ paragraph_indices: MISSING
    // ❌ chunk_type: MISSING
    // ❌ language: MISSING
    // ❌ source_type: MISSING
    "full_text": "ANNEX II\n\n...",
    "token_count": 542,
    "regulation_refs": [],
    "char_start": 0,
    "char_end": 1239
  }
}
```

## Impact on RAG Features

Using metadata from embeddings will break these RAG features:

| Feature | Requires | Impact if Missing |
|---------|----------|-------------------|
| Paragraph context extraction | `paragraph_indices` | ❌ Can't extract key paragraphs, must send full chunks (40-60% more tokens) |
| Language filtering | `language` | ❌ Can't filter by language (e.g., `--language fi` won't work) |
| Source type filtering | `source_type` | ❌ Can't filter by EU/national/international regulations |
| Chunk type filtering | `chunk_type` | ❌ Can't filter articles vs recitals |
| Cross-jurisdictional analysis | `source_type`, `language` | ❌ LLM can't identify regulation jurisdiction |

## Solution: Regenerate Embeddings

To get full metadata in embeddings, you need to:

1. **Re-run the embedding generation** with the latest processed chunks that include all new fields
2. **Update the embedding generation script** to preserve all 17 metadata fields in the output

```bash
# Example: Regenerate embeddings with full metadata
python scripts/embeddings/generate_embeddings.py \
  --input-dir processed_chunks \
  --output-prefix embeddings_vertexai_json_v2 \
  --preserve-all-metadata
```

## Configuration Update

Update `config.yaml` to use the correct metadata source:

```yaml
rag:
  metadata:
    source: "metadata_store_production.pkl"  # Built from processed_chunks
    fallback_sources:
      - "gs://bof-hackathon-data-eu/processed_chunks"  # Fallback to GCS
      - "processed_chunks"  # Fallback to local
```

## Commands Reference

```bash
# Production build (RECOMMENDED)
python scripts/utilities/build_metadata_store.py \
  --from-chunks gs://bof-hackathon-data-eu/processed_chunks \
  --output metadata_store_production.pkl

# Test build (local)
python scripts/utilities/build_metadata_store.py \
  --from-chunks processed_chunks \
  --output metadata_store_test.pkl

# Test build (GCS)
python scripts/utilities/build_metadata_store.py \
  --from-chunks gs://bof-hackathon-data-eu/test_chunks \
  --output metadata_store_test.pkl

# Legacy build from embeddings (NOT RECOMMENDED)
python scripts/utilities/build_metadata_store.py \
  --from-embeddings gs://bof-hackathon-data-eu/embeddings_vertexai_json \
  --output metadata_store_legacy.pkl

# Verify metadata store
python scripts/utilities/metadata_store.py metadata_store_production.pkl
```

## Statistics After Build

The script will show statistics about the loaded metadata:

```
Statistics:
  Total chunks: 225,345
  With paragraph indices: 105,977 (71%)
  Total paragraphs: 1,101,569

  Languages: {'en': 149927}
  Source types: {'eu_legislation': 145145, 'international_standard': 4452, 'national_law': 330}
  Chunk types: {'article': 84293, 'recital': 50161, 'mixed': 8312, 'section': 7161}
```

## Summary

✅ **DO:** Use `--from-chunks` with GCS processed_chunks for production
✅ **DO:** Verify statistics show paragraph_indices and language/source_type distributions
❌ **DON'T:** Use `--from-embeddings` unless you're okay with missing new features
⚠️ **ACTION REQUIRED:** Regenerate embeddings with full metadata if you need all RAG features in production
