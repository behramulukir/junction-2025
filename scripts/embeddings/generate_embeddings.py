#!/usr/bin/env python3
"""
Generate embeddings for preprocessed chunks using Vertex AI text-embedding-005
Uploads vectors + metadata to GCS for index building
"""

import json
import os
from pathlib import Path
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
INPUT_PREFIX = "processed_chunks/"  # Preprocessed chunks from preprocess_local.py
OUTPUT_PREFIX = "embeddings_vertexai/"  # Embeddings in Vertex AI Vector Search format


class EmbeddingGenerator:
    """Generate embeddings for EU legislation chunks using Vertex AI."""
    
    def __init__(self, project_id: str, location: str, bucket_name: str):
        """Initialize the embedding generator.
        
        Args:
            project_id: GCP project ID
            location: GCP region (e.g., us-central1)
            bucket_name: GCS bucket name
        """
        aiplatform.init(project=project_id, location=location)
        
        # Use text-multilingual-embedding-002 - Google's best performing model (768d)
        # Superior semantic understanding, 2048 token context, excellent for legal/regulatory text
        self.model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        
        print(f"Initialized EmbeddingGenerator")
        print(f"  Project: {project_id}")
        print(f"  Location: {location}")
        print(f"  Bucket: {bucket_name}")
        
    def read_chunks_from_gcs(self, prefix: str) -> Iterator[Dict]:
        """Stream JSONL chunks from GCS.
        
        Args:
            prefix: GCS prefix to read from
            
        Yields:
            Dict: Chunk metadata
        """
        blobs = list(self.bucket.list_blobs(prefix=prefix))
        jsonl_blobs = [b for b in blobs if b.name.endswith('.jsonl')]
        
        print(f"Found {len(jsonl_blobs)} JSONL files in gs://{self.bucket.name}/{prefix}")
        
        for blob in jsonl_blobs:
            print(f"Reading {blob.name}...")
            content = blob.download_as_text()
            
            for line in content.strip().split('\n'):
                if line:
                    yield json.loads(line)
    
    def prepare_text_for_embedding(self, chunk: Dict) -> str:
        """Prepare chunk text for embedding with structured metadata context.
        
        Args:
            chunk: Chunk metadata dictionary
            
        Returns:
            str: Text for embedding with metadata prefix for better semantic search
        """
        # Add structured metadata prefix for better semantic matching
        # This helps the model understand document context and improves filtering accuracy
        context_parts = []
        
        # Add document type if known
        doc_type = chunk.get('doc_type')
        if doc_type and doc_type not in ['Unknown', None, '']:
            context_parts.append(f"Type: {doc_type}")
        
        # Add year for temporal filtering
        year = chunk.get('year')
        if year and str(year) not in ['None', '']:
            context_parts.append(f"Year: {year}")
        
        # Add article/section number for precise navigation
        article_num = chunk.get('article_number')
        if article_num:
            context_parts.append(f"Article: {article_num}")
        
        # Add source type for multi-source corpus
        source_type = chunk.get('source_type', '')
        if source_type == 'national_law':
            context_parts.append("[National Law]")
        elif source_type == 'international_standard':
            context_parts.append("[International Standard]")
        
        # Combine metadata prefix with full text
        if context_parts:
            metadata_prefix = " | ".join(context_parts)
            return f"{metadata_prefix}\n\n{chunk['full_text']}"
        
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
            num_batches = (len(chunks) + 249) // 250
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
                    progress_bar.write(f"⚠️  WARNING: Single chunk with {total_tokens} tokens exceeds limit. Using zero vector.")
                    progress_bar.update(1)
                return [[0.0] * 768]
            
            mid = len(chunks) // 2
            if progress_bar is not None:
                progress_bar.write(f"📊 Batch too large ({len(chunks)} chunks, {total_tokens:,} tokens > 20K limit). Splitting: {mid} + {len(chunks) - mid}")
            first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
            second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
            return first_half + second_half
        
        # Try batch processing
        max_retries = 2
        for attempt in range(max_retries):
            try:
                embeddings = self.model.get_embeddings(texts)
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
                            progress_bar.write(f"⚠️  WARNING: Single chunk failed. Using zero vector.")
                            progress_bar.update(1)
                        return [[0.0] * 768]
                    
                    mid = len(chunks) // 2
                    if progress_bar is not None:
                        progress_bar.write(f"📊 Batch error ({len(chunks)} chunks). Splitting: {mid} + {len(chunks) - mid}")
                    first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
                    second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
                    return first_half + second_half
                elif attempt == max_retries - 1:
                    if progress_bar is not None:
                        progress_bar.write(f"❌ Failed after {max_retries} retries: {e}")
                    # Last resort: split batch
                    if len(chunks) > 1:
                        mid = len(chunks) // 2
                        first_half = self.generate_embeddings_batch(chunks[:mid], progress_bar)
                        second_half = self.generate_embeddings_batch(chunks[mid:], progress_bar)
                        return first_half + second_half
                    else:
                        # Single chunk failed completely
                        if progress_bar is not None:
                            progress_bar.update(1)
                        return [[0.0] * 768]
                if progress_bar is not None:
                    progress_bar.write(f"🔄 Retry {attempt + 1} after error: {e}")
                time.sleep(2 ** attempt)
    
    def process_and_upload(self, 
                          input_prefix: str,
                          output_prefix: str,
                          batch_size: int = 250,
                          write_interval: int = 10000):
        """Main processing loop with comprehensive progress tracking.
        
        Args:
            input_prefix: GCS prefix for input JSONL files
            output_prefix: GCS prefix for output embeddings
            batch_size: Number of chunks per API call (max 250)
            write_interval: Write to GCS after this many embeddings
        """
        chunks_buffer = []
        embeddings_output = []
        total_processed = 0
        batch_counter = 0
        total_tokens = 0
        
        print(f"\n{'='*80}")
        print(f"🚀 EMBEDDING GENERATION STARTED")
        print(f"{'='*80}")
        print(f"  Batch size: {batch_size}")
        print(f"  Write interval: {write_interval:,}")
        print(f"  Input: gs://{self.bucket.name}/{input_prefix}")
        print(f"  Output: gs://{self.bucket.name}/{output_prefix}")
        print()
        
        # Create main progress bar for chunks
        with tqdm(total=None, desc="📝 Processing chunks", unit="chunk", 
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                  dynamic_ncols=True) as pbar:
            
            # Nested progress bar for tokens
            token_pbar = tqdm(total=None, desc="🔢 Tokens processed", unit="tok", 
                            position=1, leave=False, bar_format="{desc}: {n_fmt} tokens",
                            dynamic_ncols=True)
            
            for chunk in self.read_chunks_from_gcs(input_prefix):
                chunks_buffer.append(chunk)
                chunk_tokens = chunk.get('token_count', 0)
                total_tokens += chunk_tokens
                token_pbar.update(chunk_tokens)
                
                # Process when buffer reaches batch_size
                if len(chunks_buffer) >= batch_size:
                    embeddings = self.generate_embeddings_batch(chunks_buffer, pbar)
                
                    # Combine chunk metadata with embeddings in Vertex AI Vector Search format
                    for chunk_data, embedding in zip(chunks_buffer, embeddings):
                        # Build restricts array with namespace objects (Vertex AI format)
                        restricts = []
                    
                    # Year namespace - for temporal filtering
                    year = chunk_data.get('year')
                    if year and str(year) not in ['None', 'Unknown', '']:
                        restricts.append({
                            "namespace": "year",
                            "allow": [str(year)]
                        })
                    
                    # Document type namespace - for filtering by regulation type
                    doc_type = chunk_data.get('doc_type')
                    if doc_type and str(doc_type) not in ['None', 'Unknown', '']:
                        # Sanitize: remove special chars, replace spaces with underscores, limit length
                        doc_type_clean = str(doc_type).replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')[:30]
                        restricts.append({
                            "namespace": "doc_type",
                            "allow": [doc_type_clean]
                        })
                    
                    # Source type namespace - for filtering by data source
                    source_type = chunk_data.get('source_type')
                    if source_type and str(source_type) not in ['None', 'Unknown', '']:
                        restricts.append({
                            "namespace": "source_type",
                            "allow": [str(source_type)]
                        })
                    
                    # Article number namespace - for article-level filtering
                    article_num = chunk_data.get('article_number')
                    if article_num and str(article_num) not in ['None', '']:
                        # Sanitize and limit length
                        article_clean = str(article_num).replace(' ', '_')[:30]
                        restricts.append({
                            "namespace": "article",
                            "allow": [article_clean]
                        })
                    
                    # Language namespace - for language-specific search
                    language = chunk_data.get('language')
                    if language and str(language) not in ['None', 'Unknown', '']:
                        restricts.append({
                            "namespace": "language",
                            "allow": [str(language)]
                        })
                    
                    # Create Vertex AI compatible format
                    embedding_record = {
                        'id': f"{chunk_data['document_id']}_{chunk_data['chunk_id']}",
                        'embedding': embedding
                    }
                    
                    # Add restricts only if we have valid filtering metadata
                    if restricts:
                        embedding_record['restricts'] = restricts
                    
                    # Store full metadata separately for retrieval (not used by Vertex AI index)
                    embedding_record['metadata'] = {
                        'document_id': chunk_data['document_id'],
                        'chunk_id': chunk_data['chunk_id'],
                        'filename': chunk_data['filename'],
                        'regulation_name': chunk_data['regulation_name'],
                        'year': chunk_data['year'],
                        'doc_type': chunk_data['doc_type'],
                        'article_number': chunk_data['article_number'],
                        'chunk_type': chunk_data.get('chunk_type'),
                        'source_type': chunk_data.get('source_type'),
                        'language': chunk_data.get('language'),
                        'token_count': chunk_data['token_count'],
                        'full_text': chunk_data['full_text'][:500]  # First 500 chars for preview
                    }
                    
                    embeddings_output.append(embedding_record)
                
                    total_processed += len(chunks_buffer)
                    chunks_buffer = []
                    
                    # Write to GCS every write_interval embeddings to avoid memory issues
                    if len(embeddings_output) >= write_interval:
                        pbar.write(f"💾 Writing batch {batch_counter} ({len(embeddings_output):,} embeddings)...")
                        self._write_embeddings_to_gcs(embeddings_output, output_prefix, batch_counter)
                        batch_counter += 1
                        embeddings_output = []
                    
                    # Update status in progress bar description
                    pbar.set_postfix({
                        'batches': batch_counter,
                        'tokens': f"{total_tokens:,}",
                        'buffer': len(embeddings_output)
                    })
        
            # Process remaining chunks
            if chunks_buffer:
                pbar.write(f"📦 Processing final batch ({len(chunks_buffer)} chunks)...")
                embeddings = self.generate_embeddings_batch(chunks_buffer, pbar)
            for chunk_data, embedding in zip(chunks_buffer, embeddings):
                # Build restricts array (same logic as above)
                restricts = []
                
                year = chunk_data.get('year')
                if year and str(year) not in ['None', 'Unknown', '']:
                    restricts.append({"namespace": "year", "allow": [str(year)]})
                
                doc_type = chunk_data.get('doc_type')
                if doc_type and str(doc_type) not in ['None', 'Unknown', '']:
                    doc_type_clean = str(doc_type).replace(' ', '_').replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(',', '')[:30]
                    restricts.append({"namespace": "doc_type", "allow": [doc_type_clean]})
                
                source_type = chunk_data.get('source_type')
                if source_type and str(source_type) not in ['None', 'Unknown', '']:
                    restricts.append({"namespace": "source_type", "allow": [str(source_type)]})
                
                article_num = chunk_data.get('article_number')
                if article_num and str(article_num) not in ['None', '']:
                    article_clean = str(article_num).replace(' ', '_')[:30]
                    restricts.append({"namespace": "article", "allow": [article_clean]})
                
                language = chunk_data.get('language')
                if language and str(language) not in ['None', 'Unknown', '']:
                    restricts.append({"namespace": "language", "allow": [str(language)]})
                
                embedding_record = {
                    'id': f"{chunk_data['document_id']}_{chunk_data['chunk_id']}",
                    'embedding': embedding
                }
                
                if restricts:
                    embedding_record['restricts'] = restricts
                
                embedding_record['metadata'] = {
                    'document_id': chunk_data['document_id'],
                    'chunk_id': chunk_data['chunk_id'],
                    'filename': chunk_data['filename'],
                    'regulation_name': chunk_data['regulation_name'],
                    'year': chunk_data['year'],
                    'doc_type': chunk_data['doc_type'],
                    'article_number': chunk_data['article_number'],
                    'chunk_type': chunk_data.get('chunk_type'),
                    'source_type': chunk_data.get('source_type'),
                    'language': chunk_data.get('language'),
                    'token_count': chunk_data['token_count'],
                    'full_text': chunk_data['full_text'][:500]
                }
                
                embeddings_output.append(embedding_record)
                total_processed += len(chunks_buffer)
            
            # Write final batch
            if embeddings_output:
                pbar.write(f"💾 Writing final batch {batch_counter} ({len(embeddings_output):,} embeddings)...")
                self._write_embeddings_to_gcs(embeddings_output, output_prefix, batch_counter)
            
            # Close token progress bar
            token_pbar.close()
        
        # Summary
        estimated_cost = (total_tokens * 0.000025) / 1000
        print(f"\n{'='*80}")
        print(f"✅ EMBEDDING GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total embeddings generated: {total_processed:,}")
        print(f"Total tokens processed: {total_tokens:,}")
        print(f"Estimated cost: ${estimated_cost:.2f}")
        print(f"Output location: gs://{self.bucket.name}/{output_prefix}")
        print(f"{'='*80}")
    
    def _write_embeddings_to_gcs(self, embeddings: List[Dict], prefix: str, batch_num: int):
        """Write embeddings to GCS as JSONL with upload progress.
        
        Args:
            embeddings: List of embedding dictionaries
            prefix: GCS prefix for output
            batch_num: Batch number for filename
        """
        filename = f"{prefix}embeddings_batch_{batch_num:06d}.jsonl"
        
        # Show progress for JSON serialization
        content_lines = []
        for emb in tqdm(embeddings, desc="  Serializing", leave=False, unit="emb"):
            content_lines.append(json.dumps(emb))
        content = "\n".join(content_lines)
        
        # Upload to GCS
        blob = self.bucket.blob(filename)
        size_mb = len(content) / (1024 * 1024)
        blob.upload_from_string(content)
        
        print(f"  ✓ Uploaded {filename} ({len(embeddings):,} embeddings, {size_mb:.1f} MB)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate embeddings for EU legislation chunks using Vertex AI'
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
        help='Number of chunks per API call (max 250, auto-splits if >20K tokens)'
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
