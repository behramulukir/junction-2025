#!/usr/bin/env python3
"""
Build metadata store from processed chunks or embeddings
Preserves all fields including paragraph_indices, language, source_type
"""

import json
import pickle
import sys
from pathlib import Path
from google.cloud import storage
from tqdm import tqdm

# Add utilities to path
sys.path.insert(0, str(Path(__file__).parent))
from metadata_store import MetadataStore


def build_from_processed_chunks(chunks_dir: str = "processed_chunks") -> MetadataStore:
    """Build metadata store from processed_chunks directory (local or GCS).
    
    This is the RECOMMENDED method as it preserves all fields including:
    - paragraph_indices
    - language
    - source_type
    - regulation_refs
    - token_count
    - chunk_type
    - etc.
    
    Args:
        chunks_dir: Path to processed_chunks directory (local path or gs://bucket/prefix)
        
    Returns:
        MetadataStore instance
    """
    print(f"\n{'='*80}")
    print("Building Metadata Store from Processed Chunks")
    print(f"{'='*80}\n")
    
    # Check if GCS path
    if chunks_dir.startswith('gs://'):
        store = build_from_gcs_chunks(chunks_dir)
    else:
        store = MetadataStore()
        store.load_from_processed_chunks(chunks_dir)
    
    # Show statistics
    stats = store.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total chunks: {stats['total_chunks']:,}")
    print(f"  With paragraph indices: {stats['with_paragraph_indices']:,}")
    print(f"  Total paragraphs: {stats['total_paragraphs']:,}")
    print(f"\n  Languages: {dict(stats['languages'])}")
    print(f"  Source types: {dict(stats['source_types'])}")
    print(f"  Chunk types: {dict(stats['chunk_types'])}")
    
    return store


def build_from_gcs_chunks(gcs_path: str) -> MetadataStore:
    """Build metadata store from GCS processed_chunks directory.
    
    This loads from gs://bucket/processed_chunks/ and preserves all metadata fields.
    
    Args:
        gcs_path: GCS path (gs://bucket/prefix or gs://bucket/prefix/)
        
    Returns:
        MetadataStore instance
    """
    print(f"Loading from GCS: {gcs_path}")
    
    # Parse GCS path
    gcs_path = gcs_path.rstrip('/')
    if not gcs_path.startswith('gs://'):
        raise ValueError(f"Invalid GCS path: {gcs_path}")
    
    path_parts = gcs_path[5:].split('/', 1)
    bucket_name = path_parts[0]
    prefix = path_parts[1] + '/' if len(path_parts) > 1 else ''
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # List all chunk files
    print(f"Finding chunk files in gs://{bucket_name}/{prefix}...")
    blobs = list(bucket.list_blobs(prefix=prefix))
    chunk_files = [b for b in blobs if b.name.endswith('.jsonl')]
    
    print(f"Found {len(chunk_files)} chunk files")
    print("Loading metadata...")
    
    store = MetadataStore()
    count = 0
    
    for blob in tqdm(chunk_files, desc="Processing files"):
        content = blob.download_as_text()
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            chunk = json.loads(line)
            chunk_id = f"{chunk.get('document_id')}_{chunk.get('chunk_id')}"
            
            # Store complete metadata (same as local method)
            store.metadata[chunk_id] = {
                'id': chunk_id,
                'document_id': chunk.get('document_id'),
                'filename': chunk.get('filename', ''),
                'chunk_id': chunk.get('chunk_id'),
                'chunk_type': chunk.get('chunk_type', ''),
                'full_text': chunk.get('full_text', ''),
                'regulation_name': chunk.get('regulation_name', ''),
                'year': chunk.get('year'),
                'doc_type': chunk.get('doc_type', ''),
                'article_number': chunk.get('article_number'),
                'paragraph_numbers': chunk.get('paragraph_numbers', []),
                'paragraph_indices': chunk.get('paragraph_indices', []),
                'char_start': chunk.get('char_start'),
                'char_end': chunk.get('char_end'),
                'token_count': chunk.get('token_count'),
                'regulation_refs': chunk.get('regulation_refs', []),
                'language': chunk.get('language', 'en'),
                'source_type': chunk.get('source_type', 'eu_legislation'),
                'chapter': chunk.get('chapter'),
                'section': chunk.get('section'),
            }
            count += 1
            
            if count % 10000 == 0:
                print(f"  Loaded {count} entries...")
    
    print(f"✅ Loaded {count} entries from GCS")
    return store


def build_from_embeddings_gcs(gcs_path: str) -> MetadataStore:
    """Build metadata store from GCS embeddings directory.
    
    ⚠️  WARNING: Embeddings may not contain all new fields (paragraph_indices, 
    language, source_type, chunk_type). Recommended to use build_from_processed_chunks() 
    with GCS processed_chunks path instead.
    
    This method extracts metadata from the 'metadata' field in embedding JSON files.
    Supports both .json (single JSON object per file) and .jsonl (line-delimited) formats.
    
    Args:
        gcs_path: GCS path to embeddings (gs://bucket/prefix or gs://bucket/prefix/)
        
    Returns:
        MetadataStore instance
    """
    print(f"\n{'='*80}")
    print("Building Metadata Store from GCS Embeddings")
    print(f"{'='*80}\n")
    print("⚠️  WARNING: Embeddings may not contain all new metadata fields.")
    print("⚠️  Missing fields: paragraph_indices, chunk_type, language, source_type")
    print("⚠️  Recommended: Use --from-chunks with gs://bucket/processed_chunks instead.\n")
    
    # Parse GCS path
    gcs_path = gcs_path.rstrip('/')
    if not gcs_path.startswith('gs://'):
        raise ValueError(f"Invalid GCS path: {gcs_path}")
    
    path_parts = gcs_path[5:].split('/', 1)
    bucket_name = path_parts[0]
    prefix = path_parts[1] + '/' if len(path_parts) > 1 else ''
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # List all embedding files
    print(f"Finding embedding files in gs://{bucket_name}/{prefix}...")
    blobs = list(bucket.list_blobs(prefix=prefix))
    embedding_files = [b for b in blobs if b.name.endswith('.json') or b.name.endswith('.jsonl')]
    
    print(f"Found {len(embedding_files)} embedding files")
    print("Extracting metadata...")
    
    store = MetadataStore()
    count = 0
    
    for blob in tqdm(embedding_files, desc="Processing files"):
        content = blob.download_as_text()
        
        # Try to parse as line-delimited JSON first
        lines = content.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            try:
                data = json.loads(line)
                embedding_id = data.get('id')
                
                if not embedding_id:
                    continue
                
                # Extract metadata from embedding entry
                metadata = data.get('metadata', {})
                
                # Ensure id field is set
                metadata['id'] = embedding_id
                
                # Add missing fields with defaults (these are likely not in embeddings)
                if 'paragraph_indices' not in metadata:
                    metadata['paragraph_indices'] = []
                if 'chunk_type' not in metadata:
                    metadata['chunk_type'] = 'unknown'
                if 'language' not in metadata:
                    metadata['language'] = 'en'
                if 'source_type' not in metadata:
                    metadata['source_type'] = 'eu_legislation'
                
                store.metadata[embedding_id] = metadata
                count += 1
                
                if count % 10000 == 0:
                    print(f"  Loaded {count} entries...")
                    
            except json.JSONDecodeError:
                # Skip invalid JSON lines
                continue
    
    print(f"\n✅ Built metadata store with {count:,} entries from embeddings")
    print(f"⚠️  Note: Missing fields filled with defaults\n")
    
    return store


def save_metadata_store(metadata_store, output_file: str = "metadata_store_production.pkl"):
    """Save metadata store to pickle file.
    
    Args:
        metadata_store: MetadataStore instance or dict
        output_file: Output file path
    """
    # Extract dict if MetadataStore instance
    if isinstance(metadata_store, MetadataStore):
        data = metadata_store.metadata
    else:
        data = metadata_store
    
    print(f"\nSaving metadata store to: {output_file}")
    with open(output_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"✅ Saved {len(data):,} entries")
    
    # Show sample
    if data:
        sample_id = list(data.keys())[0]
        print(f"\nSample metadata for {sample_id}:")
        for key, value in data[sample_id].items():
            if key == 'full_text':
                print(f"  {key}: '{value[:100]}...' ({len(value)} chars)")
            elif key == 'paragraph_indices':
                print(f"  {key}: {len(value)} paragraphs")
            else:
                print(f"  {key}: {value}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build metadata store from processed chunks or embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build from local processed chunks (RECOMMENDED)
  python build_metadata_store.py --from-chunks processed_chunks
  
  # Build from GCS processed chunks (RECOMMENDED for production)
  python build_metadata_store.py --from-chunks gs://bof-hackathon-data-eu/processed_chunks
  
  # Build from GCS test chunks
  python build_metadata_store.py --from-chunks gs://bof-hackathon-data-eu/test_chunks
  
  # Build from GCS embeddings (NOT RECOMMENDED - missing new fields)
  python build_metadata_store.py --from-embeddings gs://bof-hackathon-data-eu/embeddings_vertexai_json
  
  # Custom output file
  python build_metadata_store.py --from-chunks gs://bof-hackathon-data-eu/processed_chunks --output metadata_prod.pkl
        """
    )
    
    parser.add_argument(
        '--from-chunks',
        type=str,
        metavar='PATH',
        help='Build from processed_chunks (local path or gs://bucket/prefix) [RECOMMENDED]'
    )
    parser.add_argument(
        '--from-embeddings',
        type=str,
        metavar='GCS_PATH',
        help='Build from GCS embeddings (gs://bucket/prefix) [NOT RECOMMENDED - missing new fields]'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='metadata_store_production.pkl',
        help='Output pickle file path'
    )
    
    args = parser.parse_args()
    
    # Build metadata store
    if args.from_chunks:
        metadata_store = build_from_processed_chunks(args.from_chunks)
        save_metadata_store(metadata_store, args.output)
    elif args.from_embeddings:
        metadata_store = build_from_embeddings_gcs(args.from_embeddings)
        save_metadata_store(metadata_store, args.output)
    else:
        # Default: try processed_chunks if it exists
        if Path('processed_chunks').exists():
            print("No source specified, using default: processed_chunks/")
            metadata_store = build_from_processed_chunks('processed_chunks')
            save_metadata_store(metadata_store, args.output)
        else:
            parser.print_help()
            print("\nERROR: No source specified and processed_chunks/ not found")
            print("Please specify --from-chunks or --from-embeddings")
            print("\nRECOMMENDED: --from-chunks gs://bof-hackathon-data-eu/processed_chunks")
            sys.exit(1)


if __name__ == "__main__":
    main()
