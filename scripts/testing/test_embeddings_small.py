#!/usr/bin/env python3
"""
Test embedding generation on a small sample
"""
import json
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.cloud import storage

# Configuration
PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "europe-west1"
BUCKET_NAME = "bof-hackathon-data-eu"
INPUT_FILE = "test_chunks/test_chunks_small.jsonl"
OUTPUT_FILE = "test_embeddings/embeddings_small.jsonl"

def sanitize_value(value, max_length=30):
    """Sanitize metadata values for Vertex AI Vector Search."""
    if value is None:
        return None
    value_str = str(value)
    # Remove special characters that Vertex AI doesn't like
    value_str = value_str.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')
    value_str = value_str.replace(' ', '_')
    # Truncate to max length
    return value_str[:max_length]

def generate_embeddings_test():
    """Generate embeddings for test chunks."""
    print(f"Initializing Vertex AI...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print(f"Loading embedding model...")
    model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
    
    print(f"Initializing GCS client...")
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Download input file
    print(f"Downloading {INPUT_FILE}...")
    blob = bucket.blob(INPUT_FILE)
    content = blob.download_as_text()
    
    chunks = []
    for line in content.strip().split('\n'):
        if line:
            chunks.append(json.loads(line))
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Generate embeddings
    embeddings_output = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}: {chunk['document_id']}_chunk_{chunk['chunk_id']}")
        
        # Get text to embed
        text = chunk['full_text']
        
        # Generate embedding
        try:
            embeddings = model.get_embeddings([text])
            embedding_vector = embeddings[0].values
            
            print(f"  Generated embedding: {len(embedding_vector)} dimensions")
            
            # Build restricts array for Vertex AI Vector Search
            restricts = []
            
            # Add year namespace
            if chunk.get('year'):
                restricts.append({
                    "namespace": "year",
                    "allow": [str(chunk['year'])]
                })
            
            # Add doc_type namespace
            if chunk.get('doc_type') and chunk['doc_type'] != 'Unknown':
                doc_type_clean = sanitize_value(chunk['doc_type'])
                restricts.append({
                    "namespace": "doc_type",
                    "allow": [doc_type_clean]
                })
            
            # Add source_type namespace
            if chunk.get('source_type'):
                restricts.append({
                    "namespace": "source_type",
                    "allow": [chunk['source_type']]
                })
            
            # Add article namespace
            if chunk.get('article_number'):
                restricts.append({
                    "namespace": "article",
                    "allow": [str(chunk['article_number'])]
                })
            
            # Add language namespace
            if chunk.get('language'):
                restricts.append({
                    "namespace": "language",
                    "allow": [chunk['language']]
                })
            
            # Create output in Vertex AI format
            output = {
                "id": f"{chunk['document_id']}_chunk_{chunk['chunk_id']}",
                "embedding": embedding_vector,
                "restricts": restricts,
                "metadata": {
                    "document_id": chunk['document_id'],
                    "chunk_id": chunk['chunk_id'],
                    "regulation_name": chunk.get('regulation_name', ''),
                    "year": chunk.get('year'),
                    "doc_type": chunk.get('doc_type'),
                    "chunk_type": chunk.get('chunk_type'),
                    "article_number": chunk.get('article_number'),
                    "source_type": chunk.get('source_type'),
                    "language": chunk.get('language')
                }
            }
            
            embeddings_output.append(output)
            print(f"  Restricts: {len(restricts)} namespaces")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    # Upload results
    print(f"\nWriting {len(embeddings_output)} embeddings to {OUTPUT_FILE}...")
    output_content = '\n'.join([json.dumps(emb) for emb in embeddings_output])
    
    output_blob = bucket.blob(OUTPUT_FILE)
    output_blob.upload_from_string(output_content)
    
    print(f"✅ Successfully generated {len(embeddings_output)} embeddings")
    print(f"   Output: gs://{BUCKET_NAME}/{OUTPUT_FILE}")
    
    # Print sample
    if embeddings_output:
        print(f"\n📊 Sample embedding:")
        sample = embeddings_output[0]
        print(f"   ID: {sample['id']}")
        print(f"   Embedding dimensions: {len(sample['embedding'])}")
        print(f"   Restricts: {sample['restricts']}")
        print(f"   Metadata keys: {list(sample['metadata'].keys())}")

if __name__ == "__main__":
    generate_embeddings_test()
