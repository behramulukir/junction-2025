#!/usr/bin/env python3
"""
Parallel-enabled embedding generation with Cloud Run Jobs support
Automatically shards work across multiple workers using CLOUD_RUN_TASK_INDEX
"""

import json
import os
from typing import List, Dict, Iterator
from google.cloud import storage, aiplatform
from vertexai.language_models import TextEmbeddingModel
from tqdm import tqdm, trange
import time
import argparse

# Configuration
PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "us-central1"
BUCKET_NAME = "bof-hackathon-data"
INPUT_PREFIX = "vector_data/"
OUTPUT_PREFIX = "embeddings_v2/"


class EmbeddingGenerator:
    """Generate embeddings for EU legislation chunks using Vertex AI with parallel support."""
    
    def __init__(self, project_id: str, location: str, bucket_name: str):
        """Initialize the embedding generator.
        
        Args:
            project_id: GCP project ID
            location: GCP region (e.g., us-central1)
            bucket_name: GCS bucket name
        """
        # Use global endpoint for higher quota instead of regional
        aiplatform.init(
            project=project_id, 
            location="us-central1",
            api_endpoint="us-central1-aiplatform.googleapis.com"
        )
        
        # Use text-multilingual-embedding-002 - Google's best performing model (768d)
        # Superior semantic understanding, 2048 token context, excellent for legal/regulatory text
        self.model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        
        # Get worker info from Cloud Run Jobs environment variables
        self.task_index = int(os.getenv('CLOUD_RUN_TASK_INDEX', '0'))
        self.task_count = int(os.getenv('CLOUD_RUN_TASK_COUNT', '1'))
        
        print(f"Initialized EmbeddingGenerator")
        print(f"  Worker: {self.task_index + 1}/{self.task_count}")
        print(f"  Project: {project_id}")
        print(f"  Location: {location}")
        print(f"  Bucket: {bucket_name}")
    
    def read_chunks_from_gcs(self, prefix: str) -> Iterator[Dict]:
        """Stream JSONL chunks from GCS with automatic sharding across workers.
        
        Args:
            prefix: GCS prefix to read from
            
        Yields:
            Dict: Chunk metadata
        """
        blobs = list(self.bucket.list_blobs(prefix=prefix))
        jsonl_blobs = [b for b in blobs if b.name.endswith('.jsonl')]
        
        # Shard files across workers using modulo distribution
        # Worker 0 gets files 0, 10, 20, ...
        # Worker 1 gets files 1, 11, 21, ...
        my_blobs = [b for i, b in enumerate(jsonl_blobs) if i % self.task_count == self.task_index]
        
        print(f"Processing {len(my_blobs)} of {len(jsonl_blobs)} total files")
        
        for blob in my_blobs:
            print(f"Reading {blob.name}...")
            content = blob.download_as_text()
            
            for line in content.strip().split('\n'):
                if line:
                    yield json.loads(line)
    
    def prepare_text_for_embedding(self, chunk: Dict) -> str:
        """Prepare chunk text for embedding - just use raw text for speed.
        
        Args:
            chunk: Chunk metadata dictionary
            
        Returns:
            str: Text for embedding
        """
        # Use only full_text without metadata enrichment to maximize batch size
        return chunk['full_text']
    
    def generate_embeddings_batch(self, chunks: List[Dict], progress_bar=None) -> List[List[float]]:
        """Generate embeddings for a batch of chunks with intelligent batch size reduction.
        
        API Limits (per Vertex AI docs):
        - Max 250 texts per request
        - Max 20,000 total input tokens per request
        - Max 2048 tokens per individual text (auto-truncated)
        
        Args:
            chunks: List of chunk dictionaries
            progress_bar: Optional tqdm progress bar to update
            
        Returns:
            List of embedding vectors
        """
        # API enforces max 250 texts per request
        if len(chunks) > 250:
            # Split into sub-batches and process recursively
            all_embeddings = []
            for i in range(0, len(chunks), 250):
                sub_batch = chunks[i:i + 250]
                all_embeddings.extend(self.generate_embeddings_batch(sub_batch, progress_bar))
            return all_embeddings
        
        texts = [self.prepare_text_for_embedding(c) for c in chunks]
        
        # Calculate total tokens in batch
        total_tokens = sum(c.get('token_count', 0) for c in chunks)
        
        # Check token limit BEFORE making API call (20K token limit per request)
        if total_tokens > 20000:
            # Preemptively split batch to avoid API error
            if len(chunks) == 1:
                # Single chunk too large - shouldn't happen with 2048 token limit per chunk
                if progress_bar is not None:
                    progress_bar.write(f"⚠️  Worker {self.task_index}: Single chunk with {total_tokens} tokens exceeds limit. Using zero vector.")
                    progress_bar.update(1)
                return [[0.0] * 768]
            
            mid = len(chunks) // 2
            if progress_bar is not None:
                progress_bar.write(f"📊 Worker {self.task_index}: Batch too large ({len(chunks)} chunks, {total_tokens:,} tokens > 20K limit). Splitting: {mid} + {len(chunks) - mid}")
            first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
            second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
            return first_half + second_half
        
        # Try batch processing
        max_retries = 3
        for attempt in range(max_retries):
            try:
                embeddings = self.model.get_embeddings(texts)
                # Add small delay to avoid quota issues
                time.sleep(0.1)
                # Update progress bar if provided
                if progress_bar is not None:
                    progress_bar.update(len(chunks))
                return [emb.values for emb in embeddings]
            except Exception as e:
                error_msg = str(e)
                if "token" in error_msg.lower() or "limit" in error_msg.lower():
                    # Token limit exceeded (shouldn't happen with pre-check, but handle anyway)
                    # Split batch in half and process recursively
                    if len(chunks) == 1:
                        # Single chunk too large
                        if progress_bar is not None:
                            progress_bar.write(f"⚠️  Worker {self.task_index}: Single chunk failed. Using zero vector.")
                            progress_bar.update(1)
                        return [[0.0] * 768]
                    
                    mid = len(chunks) // 2
                    if progress_bar is not None:
                        progress_bar.write(f"📊 Worker {self.task_index}: Batch error ({len(chunks)} chunks). Splitting: {mid} + {len(chunks) - mid}")
                    first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
                    second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
                    return first_half + second_half
                elif "429" in error_msg or "quota" in error_msg.lower():
                    # Quota exceeded - wait with exponential backoff
                    wait_time = min(60, (2 ** attempt) * 5)
                    if progress_bar is not None:
                        progress_bar.write(f"⏳ Worker {self.task_index}: Quota exceeded, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    if attempt == max_retries - 1:
                        # Last resort: split batch
                        if len(chunks) > 1:
                            mid = len(chunks) // 2
                            first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
                            second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
                            return first_half + second_half
                        else:
                            if progress_bar is not None:
                                progress_bar.update(1)
                            return [[0.0] * 768]
                elif attempt == max_retries - 1:
                    if progress_bar is not None:
                        progress_bar.write(f"❌ Worker {self.task_index}: Failed after {max_retries} retries: {e}")
                    # Last resort: split batch
                    if len(chunks) > 1:
                        mid = len(chunks) // 2
                        first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
                        second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
                        return first_half + second_half
                    else:
                        if progress_bar is not None:
                            progress_bar.update(1)
                        return [[0.0] * 768]
                else:
                    if progress_bar is not None:
                        progress_bar.write(f"🔄 Worker {self.task_index}: Retry {attempt + 1} after error: {e}")
                    time.sleep(2 ** attempt)
    
    def process_and_upload(self, 
                          input_prefix: str,
                          output_prefix: str,
                          batch_size: int = 100,
                          write_interval: int = 10000):
        """Main processing loop.
        
        Args:
            input_prefix: GCS prefix for input JSONL files
            output_prefix: GCS prefix for output embeddings
            batch_size: Number of chunks per API call
            write_interval: Write to GCS after this many embeddings
        """
        chunks_buffer = []
        embeddings_output = []
        total_processed = 0
        # Start batch counter based on worker ID to avoid filename collisions
        batch_counter = self.task_index
        total_tokens = 0
        
        print(f"\n{'='*80}")
        print(f"🚀 WORKER {self.task_index + 1}/{self.task_count} STARTED")
        print(f"{'='*80}")
        print(f"  Batch size: {batch_size}")
        print(f"  Write interval: {write_interval:,}")
        print(f"  Input: gs://{self.bucket.name}/{input_prefix}")
        print(f"  Output: gs://{self.bucket.name}/{output_prefix}")
        print()
        
        # Create main progress bar for chunks
        with tqdm(total=None, desc=f"📝 Worker {self.task_index} chunks", unit="chunk",
                  position=self.task_index * 2, 
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                  dynamic_ncols=True, leave=True) as pbar:
            
            # Nested progress bar for tokens
            token_pbar = tqdm(total=None, desc=f"🔢 Worker {self.task_index} tokens", unit="tok",
                            position=self.task_index * 2 + 1, leave=False, 
                            bar_format="{desc}: {n_fmt} tokens",
                            dynamic_ncols=True)
            
            for chunk in self.read_chunks_from_gcs(input_prefix):
                chunks_buffer.append(chunk)
                chunk_tokens = chunk.get('token_count', 0)
                total_tokens += chunk_tokens
                token_pbar.update(chunk_tokens)
                
                # Process when buffer reaches batch_size
                if len(chunks_buffer) >= batch_size:
                    embeddings = self.generate_embeddings_batch(chunks_buffer, pbar)
                    
                    # Combine chunk metadata with embeddings
                    for chunk_data, embedding in zip(chunks_buffer, embeddings):
                        embeddings_output.append({
                            'id': f"{chunk_data['document_id']}_{chunk_data['chunk_id']}",
                            'embedding': embedding,
                            'metadata': {
                                'document_id': chunk_data['document_id'],
                                'chunk_id': chunk_data['chunk_id'],
                                'filename': chunk_data['filename'],
                                'regulation_name': chunk_data['regulation_name'],
                                'year': chunk_data['year'],
                                'doc_type': chunk_data['doc_type'],
                                'article_number': chunk_data['article_number'],
                                'paragraph_numbers': chunk_data['paragraph_numbers'],
                                'full_text': chunk_data['full_text'],
                                'token_count': chunk_data['token_count'],
                                'regulation_refs': chunk_data['regulation_refs'],
                                'char_start': chunk_data['char_start'],
                                'char_end': chunk_data['char_end']
                            }
                        })
                    
                    total_processed += len(chunks_buffer)
                    chunks_buffer = []
                    
                    # Write to GCS every write_interval embeddings to avoid memory issues
                    if len(embeddings_output) >= write_interval:
                        pbar.write(f"💾 Worker {self.task_index}: Writing batch {batch_counter} ({len(embeddings_output):,} embeddings)...")
                        self._write_embeddings_to_gcs(embeddings_output, output_prefix, batch_counter)
                        # Increment by task_count to avoid collisions between workers
                        batch_counter += self.task_count
                        embeddings_output = []
                    
                    # Update status in progress bar
                    pbar.set_postfix({
                        'batches': (batch_counter - self.task_index) // self.task_count,
                        'tokens': f"{total_tokens:,}",
                        'buffer': len(embeddings_output)
                    })
        
            # Process remaining chunks
            if chunks_buffer:
                pbar.write(f"📦 Worker {self.task_index}: Processing final batch ({len(chunks_buffer)} chunks)...")
                embeddings = self.generate_embeddings_batch(chunks_buffer, pbar)
                for chunk_data, embedding in zip(chunks_buffer, embeddings):
                    embeddings_output.append({
                        'id': f"{chunk_data['document_id']}_{chunk_data['chunk_id']}",
                        'embedding': embedding,
                        'metadata': chunk_data
                    })
                total_processed += len(chunks_buffer)
            
            # Write final batch
            if embeddings_output:
                pbar.write(f"💾 Worker {self.task_index}: Writing final batch {batch_counter} ({len(embeddings_output):,} embeddings)...")
                self._write_embeddings_to_gcs(embeddings_output, output_prefix, batch_counter)
            
            # Close token progress bar
            token_pbar.close()
        
        # Summary
        estimated_cost = (total_tokens * 0.000025) / 1000
        print(f"\n{'='*80}")
        print(f"✅ WORKER {self.task_index + 1}/{self.task_count} COMPLETE")
        print(f"{'='*80}")
        print(f"Total embeddings generated: {total_processed:,}")
        print(f"Total tokens processed: {total_tokens:,}")
        print(f"Estimated cost: ${estimated_cost:.2f}")
        print(f"Output location: gs://{self.bucket.name}/{output_prefix}")
        print(f"{'='*80}")
    
    def _write_embeddings_to_gcs(self, embeddings: List[Dict], prefix: str, batch_num: int):
        """Write embeddings to GCS as JSONL with worker-specific naming and upload progress.
        
        Args:
            embeddings: List of embedding dictionaries
            prefix: GCS prefix for output
            batch_num: Batch number for filename
        """
        # Include worker ID in filename to prevent collisions
        filename = f"{prefix}embeddings_worker{self.task_index:02d}_batch_{batch_num:06d}.jsonl"
        
        # Show progress for JSON serialization
        content_lines = []
        for emb in tqdm(embeddings, desc=f"  W{self.task_index} Serializing", leave=False, unit="emb", position=self.task_index * 2 + 1):
            content_lines.append(json.dumps(emb))
        content = "\n".join(content_lines)
        
        # Upload to GCS
        blob = self.bucket.blob(filename)
        size_mb = len(content) / (1024 * 1024)
        blob.upload_from_string(content)
        
        print(f"  ✓ Worker {self.task_index}: Uploaded {filename} ({len(embeddings):,} embeddings, {size_mb:.1f} MB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate embeddings for EU legislation chunks using Vertex AI (parallel-enabled)'
    )
    parser.add_argument(
        '--project-id',
        type=str,
        default=PROJECT_ID,
        help='GCP project ID'
    )
    parser.add_argument(
        '--location',
        type=str,
        default=LOCATION,
        help='GCP region (e.g., us-central1)'
    )
    parser.add_argument(
        '--bucket-name',
        type=str,
        default=BUCKET_NAME,
        help='GCS bucket name'
    )
    parser.add_argument(
        '--input-prefix',
        type=str,
        default=INPUT_PREFIX,
        help='GCS prefix for input JSONL files'
    )
    parser.add_argument(
        '--output-prefix',
        type=str,
        default=OUTPUT_PREFIX,
        help='GCS prefix for output embeddings'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of chunks per API call'
    )
    parser.add_argument(
        '--write-interval',
        type=int,
        default=10000,
        help='Write to GCS after this many embeddings'
    )
    
    args = parser.parse_args()
    
    generator = EmbeddingGenerator(
        project_id=args.project_id,
        location=args.location,
        bucket_name=args.bucket_name
    )
    
    generator.process_and_upload(
        input_prefix=args.input_prefix,
        output_prefix=args.output_prefix,
        batch_size=args.batch_size,
        write_interval=args.write_interval
    )


if __name__ == "__main__":
    main()
