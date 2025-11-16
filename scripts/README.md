# Scripts Directory

Organized scripts for the EU Legislation RAG Pipeline.

## Directory Structure

### 📂 preprocessing/
Document preprocessing and chunking scripts:
- `preprocess_local.py` - Main preprocessing script with paragraph indices
- `preprocess_and_upload.py` - Preprocessing with GCS upload

**Usage:**
```bash
python scripts/preprocessing/preprocess_local.py --config config.yaml --skip-upload
```

### 📂 embeddings/
Embedding generation scripts:
- `generate_embeddings.py` - Main embedding generation with Vertex AI format
- `generate_embeddings_parallel.py` - Parallel processing for large datasets

**Usage:**
```bash
python scripts/embeddings/generate_embeddings.py \
  --input-prefix processed_chunks/ \
  --output-prefix embeddings_vertexai/
```

### 📂 deployment/
Deployment and infrastructure scripts:
- `build_vector_index.py` - Build Vertex AI Vector Search index
- `deploy_quick.py` - Quick deployment script
- `check_deployment.py` - Verify deployment status

**Usage:**
```bash
python scripts/deployment/build_vector_index.py \
  --embeddings-prefix embeddings_vertexai/ \
  --index-display-name eu-legislation-index
```

### 📂 testing/
Testing and validation scripts:
- `test_comprehensive.py` - Comprehensive preprocessing tests
- `test_embedding_format.py` - Validate Vertex AI format
- `test_preprocessing.py` - Unit tests for preprocessing
- `validate_pipeline.py` - End-to-end pipeline validation

**Usage:**
```bash
python scripts/testing/test_comprehensive.py
python scripts/testing/validate_pipeline.py
```

### 📂 utilities/
Utility and helper scripts:
- `extract_paragraphs.py` - Extract and verify paragraph indices
- `metadata_store.py` - Metadata storage utilities
- `rag_search.py` - RAG search implementation
- `monitor_build.sh` - Monitor build progress

**Usage:**
```bash
python scripts/utilities/extract_paragraphs.py processed_chunks/chunks_batch_000000.jsonl 0
```

## Quick Start

1. **Preprocess documents:**
   ```bash
   python scripts/preprocessing/preprocess_local.py --config config.yaml --skip-upload
   ```

2. **Generate embeddings:**
   ```bash
   python scripts/embeddings/generate_embeddings.py
   ```

3. **Validate pipeline:**
   ```bash
   python scripts/testing/validate_pipeline.py
   ```

4. **Deploy index:**
   ```bash
   python scripts/deployment/build_vector_index.py
   ```

## Dependencies

All scripts use the requirements from root:
- `requirements.txt` - Core dependencies
- `requirements_vertexai.txt` - Vertex AI specific dependencies
