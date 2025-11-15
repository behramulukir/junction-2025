#!/usr/bin/env python3
"""
Build metadata store from original embeddings with metadata included
"""

import json
from google.cloud import storage
from tqdm import tqdm
import pickle

def build_metadata_store():
    """Build metadata store from original embeddings."""
    client = storage.Client()
    bucket = client.bucket("bof-hackathon-data")
    
    # List all embedding files
    print("Finding embedding files...")
    blobs = list(bucket.list_blobs(prefix="embeddings/"))
    embedding_files = [b for b in blobs if b.name.endswith('.jsonl')]
    
    print(f"Found {len(embedding_files)} embedding files")
    print("Extracting metadata...")
    
    metadata_store = {}
    
    for blob in tqdm(embedding_files, desc="Processing files"):
        content = blob.download_as_text()
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            data = json.loads(line)
            embedding_id = data['id']
            metadata = data['metadata']
            
            # Store metadata
            metadata_store[embedding_id] = metadata
    
    print(f"\n✅ Built metadata store with {len(metadata_store):,} entries")
    
    # Save to file
    output_file = "metadata_store_production.pkl"
    with open(output_file, 'wb') as f:
        pickle.dump(metadata_store, f)
    
    print(f"Saved to: {output_file}")
    
    # Show sample
    sample_id = list(metadata_store.keys())[0]
    print(f"\nSample metadata for {sample_id}:")
    for key, value in metadata_store[sample_id].items():
        if key != 'full_text':  # Skip full text for brevity
            print(f"  {key}: {value}")
    
    return metadata_store

if __name__ == "__main__":
    build_metadata_store()
