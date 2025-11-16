# EU Legislation RAG System

**Production-ready RAG system for EU legislation, national laws, and international standards**

Comprehensive pipeline for processing, embedding, and indexing regulatory documents using Google Cloud Vertex AI Vector Search.

## 📊 Current Status

- **Documents Processed**: 61,072 files
- **Total Chunks**: 334,000+ chunks (919 MB)
- **Storage**: `gs://bof-hackathon-data-eu` (EU West 1)
- **Embedding Model**: text-multilingual-embedding-002 (768-dim)
- **Features**: Paragraph indices, 5-namespace filtering, semantic chunking

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements_vertexai.txt

# Authenticate with GCP
gcloud auth application-default login
gcloud config set project nimble-granite-478311-u2
```

### 2. Preprocess Documents

```bash
python scripts/preprocessing/preprocess_local.py \
  --config config.yaml \
  --skip-upload
```

### 3. Generate Embeddings

```bash
python scripts/embeddings/generate_embeddings.py \
  --input-prefix processed_chunks/ \
  --output-prefix embeddings_vertexai/
```

### 4. Build Vector Index

```bash
python scripts/deployment/build_vector_index.py \
  --embeddings-prefix embeddings_vertexai/ \
  --index-display-name eu-legislation-index
```

## 📁 Project Structure

```
.
├── config.yaml                    # Pipeline configuration
├── Dockerfile                     # Container deployment
├── requirements.txt               # Core dependencies
├── requirements_vertexai.txt      # Vertex AI dependencies
│
├── scripts/                       # Organized scripts
│   ├── preprocessing/            # Document preprocessing
│   │   ├── preprocess_local.py   # Main preprocessing with paragraph indices
│   │   └── preprocess_and_upload.py
│   ├── embeddings/               # Embedding generation
│   │   ├── generate_embeddings.py     # Vertex AI format output
│   │   └── generate_embeddings_parallel.py
│   ├── deployment/               # Infrastructure deployment
│   │   ├── build_vector_index.py
│   │   ├── deploy_quick.py
│   │   └── check_deployment.py
│   ├── testing/                  # Tests and validation
│   │   ├── test_comprehensive.py
│   │   ├── test_embedding_format.py
│   │   └── validate_pipeline.py
│   └── utilities/                # Helper utilities
│       ├── extract_paragraphs.py
│       ├── rag_search.py
│       └── metadata_store.py
│
├── docs/                          # Documentation
│   ├── QUICK_START.md            # Getting started guide
│   ├── VERTEX_AI_INTEGRATION.md  # Format specification
│   ├── PARAGRAPH_INDICES_README.md
│   └── IMPLEMENTATION_GUIDE.md
│
├── archive/                       # Obsolete/deprecated files
│   ├── convert_embeddings_format.py
│   └── convert_test_embeddings.py
│
└── [data directories]/
    ├── output/                    # EU legislation (61K+ files)
    ├── other_national_laws/       # Finnish laws
    ├── other_regulation_standards/ # Basel, IFRS, etc.
    └── processed_chunks/          # Output chunks (334 batches)
```

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
gcp:
  bucket_name: "bof-hackathon-data-eu"  # EU West 1 bucket
  output_prefix: "processed_chunks"

processing:
  chunk_target_tokens: 1200     # Optimized for 2048 context
  min_chunk_tokens: 400
  max_chunk_tokens: 1800
  
  input_directories:
    - "output"                   # EU legislation
    - "other_national_laws"      # Finnish laws
    - "other_regulation_standards"  # International standards
```

## ✨ Key Features

### 1. **Paragraph Indices**
Every chunk tracks paragraph positions for precise extraction:
```python
{
  "paragraph_indices": [[159, 538], [539, 579], ...],
  "full_text": "Document content..."
}
```

### 2. **Vertex AI Vector Search Format**
Direct output without conversion scripts:
```json
{
  "id": "doc_id_chunk_0",
  "embedding": [768 floats],
  "restricts": [
    {"namespace": "year", "allow": ["2016"]},
    {"namespace": "doc_type", "allow": ["regulation"]},
    {"namespace": "source_type", "allow": ["eu_legislation"]}
  ],
  "metadata": {...}
}
```

### 3. **Multi-Source Support**
- EU Legislation (UUID structure)
- Finnish National Laws (.di.json)
- International Standards (Basel, IFRS, etc.)

### 4. **Smart Chunking**
- Article-aware boundaries
- Orphan merging (200 tokens)
- Cross-reference preservation
- Multi-language support (EN, FI)

## 📝 Testing

```bash
# Comprehensive preprocessing test
python scripts/testing/test_comprehensive.py

# Validate Vertex AI format
python scripts/testing/test_embedding_format.py

# End-to-end pipeline validation
python scripts/testing/validate_pipeline.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running
- **[Vertex AI Integration](docs/VERTEX_AI_INTEGRATION.md)** - Format specification
- **[Paragraph Indices](docs/PARAGRAPH_INDICES_README.md)** - Implementation details
- **[Pipeline Compatibility](docs/PIPELINE_COMPATIBILITY_SUMMARY.md)** - Architecture
- **[Scripts README](scripts/README.md)** - Script usage guide

## 🛠️ Troubleshooting

### Paragraph Indices Validation
```bash
python scripts/utilities/extract_paragraphs.py \
  processed_chunks/chunks_batch_000000.jsonl 0
```

### Check Pipeline Status
```bash
python scripts/testing/validate_pipeline.py
```

### Monitor Embedding Generation
```bash
bash scripts/utilities/monitor_build.sh
```

## 📊 Pipeline Metrics

| Metric | Value |
|--------|-------|
| Total Documents | 61,072 |
| Total Chunks | 334,000+ |
| Average Chunk Size | 1,200 tokens |
| Namespace Coverage | 4.0 avg |
| Metadata Extraction | 100% (EU), 100% (National) |
| Storage Location | EU West 1 |
| Format Compliance | 100% |

## 🔐 Data Compliance

- **Region**: EU West 1 (europe-west1)
- **Bucket**: Uniform bucket-level access
- **Soft Delete**: 7-day retention policy
- **Storage Class**: STANDARD

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contributing guidelines]

## 📧 Contact

[Add contact information]
