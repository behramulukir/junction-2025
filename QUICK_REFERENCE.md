# Quick Reference Card

## 🚀 Common Commands

### Preprocessing
```bash
# Full preprocessing run
python scripts/preprocessing/preprocess_local.py --config config.yaml --skip-upload

# With upload to GCS
python scripts/preprocessing/preprocess_and_upload.py --config config.yaml
```

### Embeddings
```bash
# Generate embeddings (Vertex AI format)
python scripts/embeddings/generate_embeddings.py \
  --input-prefix processed_chunks/ \
  --output-prefix embeddings_vertexai/

# Parallel processing
python scripts/embeddings/generate_embeddings_parallel.py
```

### Testing
```bash
# Run all tests
python scripts/testing/test_comprehensive.py
python scripts/testing/test_embedding_format.py
python scripts/testing/validate_pipeline.py

# Verify paragraph indices
python scripts/utilities/extract_paragraphs.py \
  processed_chunks/chunks_batch_000000.jsonl 0
```

### Deployment
```bash
# Build Vertex AI index
python scripts/deployment/build_vector_index.py \
  --embeddings-prefix embeddings_vertexai/ \
  --index-display-name eu-legislation-index

# Check deployment status
python scripts/deployment/check_deployment.py
```

## 📂 Directory Quick Guide

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `scripts/preprocessing/` | Document processing | `preprocess_local.py` |
| `scripts/embeddings/` | Embedding generation | `generate_embeddings.py` |
| `scripts/deployment/` | Infrastructure | `build_vector_index.py` |
| `scripts/testing/` | Tests & validation | `validate_pipeline.py` |
| `scripts/utilities/` | Helper tools | `extract_paragraphs.py` |
| `docs/` | Documentation | `QUICK_START.md` |
| `archive/` | Deprecated files | Old scripts |

## 📊 Data Locations

| Location | Size | Description |
|----------|------|-------------|
| `output/` | 710 MB | EU legislation (61K files) |
| `other_national_laws/` | 656 KB | Finnish laws |
| `other_regulation_standards/` | 21 MB | International standards |
| `processed_chunks/` | 886 MB | Output chunks (334 batches) |
| `gs://bof-hackathon-data-eu/` | 919 MB | GCS storage (EU West 1) |

## 🔧 Configuration Files

- `config.yaml` - Main pipeline configuration
- `requirements.txt` - Core Python dependencies
- `requirements_vertexai.txt` - Vertex AI dependencies
- `Dockerfile` - Container configuration

## 📝 Important Documentation

- `README.md` - Main project documentation
- `docs/QUICK_START.md` - Getting started guide
- `docs/VERTEX_AI_INTEGRATION.md` - Vector Search format
- `docs/PARAGRAPH_INDICES_README.md` - Paragraph indices
- `scripts/README.md` - Script usage guide
- `DIRECTORY_STRUCTURE.txt` - Full directory tree

## 🎯 Quick Tasks

### Check Pipeline Status
```bash
python scripts/testing/validate_pipeline.py
```

### Validate Chunks
```bash
ls -lh processed_chunks/ | wc -l
```

### Check GCS Upload
```bash
gcloud storage ls gs://bof-hackathon-data-eu/processed_chunks/
```

### Monitor Processing
```bash
tail -f preprocessingnew.log
```

## 🐛 Troubleshooting

### Import Errors
Scripts moved - use full paths:
```bash
python scripts/preprocessing/preprocess_local.py
```

### GCS Access Issues
```bash
gcloud auth application-default login
gcloud config set project nimble-granite-478311-u2
```

### Check Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements_vertexai.txt
```

## 📦 Pipeline Workflow

1. **Preprocess** → `scripts/preprocessing/preprocess_local.py`
2. **Test** → `scripts/testing/test_comprehensive.py`
3. **Generate Embeddings** → `scripts/embeddings/generate_embeddings.py`
4. **Validate Format** → `scripts/testing/test_embedding_format.py`
5. **Deploy Index** → `scripts/deployment/build_vector_index.py`

## 🔗 External Resources

- GCS Bucket: `gs://bof-hackathon-data-eu`
- GCP Project: `nimble-granite-478311-u2`
- Region: `europe-west1` (EU West 1)
- Embedding Model: `text-multilingual-embedding-002`
