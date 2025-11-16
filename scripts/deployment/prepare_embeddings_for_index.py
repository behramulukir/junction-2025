#!/usr/bin/env python3
"""
Prepare embeddings for Vertex AI Vector Search by renaming .jsonl to .json
Vertex AI Vector Search requires .json, .csv, or .avro extensions
"""

from google.cloud import storage
import argparse

def rename_embeddings_for_vertex(
    bucket_name: str,
    source_prefix: str,
    dest_prefix: str
):
    """Copy .jsonl files to .json for Vertex AI compatibility.
    
    Args:
        bucket_name: GCS bucket name
        source_prefix: Source prefix with .jsonl files
        dest_prefix: Destination prefix for .json files
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    print(f"Scanning gs://{bucket_name}/{source_prefix}")
    
    # List all .jsonl files
    blobs = list(bucket.list_blobs(prefix=source_prefix))
    jsonl_files = [b for b in blobs if b.name.endswith('.jsonl')]
    
    print(f"Found {len(jsonl_files)} .jsonl files")
    
    if len(jsonl_files) == 0:
        print("No .jsonl files found!")
        return
    
    # Copy each file with .json extension
    for i, source_blob in enumerate(jsonl_files, 1):
        # Get filename without path and extension
        filename = source_blob.name.split('/')[-1].replace('.jsonl', '.json')
        dest_blob_name = f"{dest_prefix.rstrip('/')}/{filename}"
        
        # Copy (rename) the file
        dest_blob = bucket.copy_blob(
            source_blob,
            bucket,
            dest_blob_name
        )
        
        print(f"[{i}/{len(jsonl_files)}] {source_blob.name} -> {dest_blob_name}")
    
    print(f"\n{'='*80}")
    print(f"COMPLETE!")
    print(f"{'='*80}")
    print(f"Embeddings ready at: gs://{bucket_name}/{dest_prefix}")
    print(f"Total files: {len(jsonl_files)}")
    print(f"\nUse this path in your index creation:")
    print(f"  --embeddings-prefix {dest_prefix}")


def main():
    parser = argparse.ArgumentParser(
        description='Prepare embeddings for Vertex AI Vector Search'
    )
    parser.add_argument(
        '--bucket-name',
        type=str,
        default='bof-hackathon-data-eu',
        help='GCS bucket name'
    )
    parser.add_argument(
        '--source-prefix',
        type=str,
        default='embeddings_vertexai/',
        help='Source prefix with .jsonl files'
    )
    parser.add_argument(
        '--dest-prefix',
        type=str,
        default='embeddings_vertexai_json/',
        help='Destination prefix for .json files'
    )
    
    args = parser.parse_args()
    
    rename_embeddings_for_vertex(
        bucket_name=args.bucket_name,
        source_prefix=args.source_prefix,
        dest_prefix=args.dest_prefix
    )


if __name__ == "__main__":
    main()
