#!/usr/bin/env python3
"""
EU Legislation Document Preprocessing Pipeline

This script:
1. Scans the workspace for EU legislation JSON files
2. Filters out non-content files (*.doc.json, *.toc.fmx.json)
3. Chunks documents by semantic boundaries (Articles, Recitals)
4. Extracts metadata (regulation names, article numbers, citations)
5. Uploads processed chunks to Google Cloud Storage as JSONL

Usage:
    python preprocess_and_upload.py --config config.yaml
"""

import json
import re
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import yaml
import tiktoken
from tqdm import tqdm
from google.cloud import storage


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""
    document_id: str  # UUID from directory
    filename: str  # Original filename
    regulation_name: str  # Extracted regulation name
    year: Optional[int]  # Extracted year
    doc_type: str  # e.g., "Commission Implementing Regulation"
    chunk_id: int  # Sequential chunk number within document
    chunk_type: str  # "article", "recital", "annex", "mixed"
    article_number: Optional[str]  # e.g., "5"
    paragraph_numbers: List[str]  # e.g., ["(5)", "(6)"]
    full_text: str  # The actual chunk text
    char_start: int  # Character offset in original document
    char_end: int  # Character offset end
    token_count: int  # Approximate token count
    regulation_refs: List[str]  # Referenced regulations (e.g., ["EC No 1334/2003"])


@dataclass
class DocumentInfo:
    """Information about a source document."""
    document_id: str
    filename: str
    file_path: str
    paragraphs: List[str]
    full_text: str


# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Configuration loader."""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get(self, *keys, default=None):
        """Get nested config value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value


# ============================================================================
# Document Scanner & Filter
# ============================================================================

class DocumentScanner:
    """Scans workspace and filters JSON files."""
    
    def __init__(self, base_path: str, exclude_patterns: List[str]):
        self.base_path = Path(base_path)
        self.exclude_patterns = exclude_patterns
        self.logger = logging.getLogger(__name__)
    
    def scan(self) -> List[Path]:
        """Scan and return all valid JSON files."""
        self.logger.info(f"Scanning directory: {self.base_path}")
        
        all_files = list(self.base_path.rglob("*.json"))
        self.logger.info(f"Found {len(all_files)} total JSON files")
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in all_files:
            if not any(file_path.match(pattern) for pattern in self.exclude_patterns):
                filtered_files.append(file_path)
        
        self.logger.info(f"After filtering: {len(filtered_files)} files remain")
        return filtered_files
    
    def load_document(self, file_path: Path) -> Optional[DocumentInfo]:
        """Load and parse a JSON document."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract paragraphs from pages
            paragraphs = []
            for page in data.get('pages', []):
                paragraphs.extend(page.get('paragraphs', []))
            
            if not paragraphs:
                self.logger.warning(f"No paragraphs found in {file_path}")
                return None
            
            # Extract document ID from path (UUID directory)
            # Path structure: .../output/{UUID}/fmx4/{filename}.json
            parts = file_path.parts
            uuid_idx = parts.index('output') + 1 if 'output' in parts else -2
            document_id = parts[uuid_idx]
            
            full_text = "\n".join(paragraphs)
            
            return DocumentInfo(
                document_id=document_id,
                filename=file_path.name,
                file_path=str(file_path),
                paragraphs=paragraphs,
                full_text=full_text
            )
        
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return None


# ============================================================================
# Metadata Extractor
# ============================================================================

class MetadataExtractor:
    """Extracts regulation names, years, document types, and references."""
    
    # Regex patterns
    REGULATION_PATTERN = re.compile(
        r'(Commission|Council|European Parliament|Directive|Regulation|Decision|Corrigendum to)\s+'
        r'(?:Implementing\s+|Delegated\s+|Amending\s+)*'
        r'(Regulation|Directive|Decision)\s+'
        r'\((EU|EC|EEC)\)\s+'
        r'(?:No\s+)?'
        r'(\d{4}/\d+|\d+/\d{4})',
        re.IGNORECASE
    )
    
    YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')
    
    DOC_TYPE_PATTERN = re.compile(
        r'^(Commission|Council|European Parliament)?\s*'
        r'(Implementing|Delegated|Amending)?\s*'
        r'(Regulation|Directive|Decision|Corrigendum)',
        re.IGNORECASE
    )
    
    REF_PATTERN = re.compile(
        r'\((EU|EC|EEC)\)\s+(?:No\s+)?(\d{4}/\d+|\d+/\d{4})',
        re.IGNORECASE
    )
    
    @staticmethod
    def extract_regulation_name(first_paragraph: str) -> str:
        """Extract the main regulation name from first paragraph."""
        match = MetadataExtractor.REGULATION_PATTERN.search(first_paragraph)
        if match:
            return match.group(0)
        
        # Fallback: use first 100 chars
        return first_paragraph[:100].strip()
    
    @staticmethod
    def extract_year(text: str) -> Optional[int]:
        """Extract year from text."""
        matches = MetadataExtractor.YEAR_PATTERN.findall(text)
        if matches:
            # Return the most recent year found
            years = [int(m[0] + m[1:]) for m in matches]
            return max(years)
        return None
    
    @staticmethod
    def extract_doc_type(first_paragraph: str) -> str:
        """Extract document type."""
        match = MetadataExtractor.DOC_TYPE_PATTERN.search(first_paragraph)
        if match:
            parts = [p for p in match.groups() if p]
            return " ".join(parts)
        return "Unknown"
    
    @staticmethod
    def extract_regulation_refs(text: str) -> List[str]:
        """Extract all regulation references from text."""
        matches = MetadataExtractor.REF_PATTERN.findall(text)
        refs = set()
        for match in matches:
            refs.add(f"{match[0]} No {match[1]}")
        return sorted(list(refs))


# ============================================================================
# Document Chunker
# ============================================================================

class DocumentChunker:
    """Chunks documents by semantic boundaries."""
    
    def __init__(self, config: Config):
        self.article_pattern = re.compile(config.get('chunking', 'article_pattern'))
        self.recital_pattern = re.compile(config.get('chunking', 'recital_pattern'))
        self.section_pattern = re.compile(config.get('chunking', 'section_pattern'))
        
        self.chunk_target_tokens = config.get('processing', 'chunk_target_tokens')
        self.min_chunk_tokens = config.get('processing', 'min_chunk_tokens')
        self.max_chunk_tokens = config.get('processing', 'max_chunk_tokens')
        self.merge_orphans = config.get('chunking', 'merge_orphans')
        self.orphan_threshold = config.get('chunking', 'orphan_threshold')
        
        # Token counter
        self.encoder = tiktoken.get_encoding("cl100k_base")
        
        self.logger = logging.getLogger(__name__)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
    
    def detect_boundary(self, paragraph: str) -> Tuple[str, Optional[str], List[str]]:
        """
        Detect if paragraph is a structural boundary.
        
        Returns:
            (chunk_type, article_number, paragraph_numbers)
        """
        # Check for Article
        if self.article_pattern.match(paragraph):
            article_match = re.search(r'Article\s+(\d+)', paragraph)
            article_num = article_match.group(1) if article_match else None
            return ("article", article_num, [])
        
        # Check for Recital
        if self.recital_pattern.match(paragraph):
            recital_match = re.search(r'\((\d+)\)', paragraph)
            recital_num = f"({recital_match.group(1)})" if recital_match else None
            return ("recital", None, [recital_num] if recital_num else [])
        
        # Check for Section
        if self.section_pattern.match(paragraph):
            return ("section", None, [])
        
        return ("paragraph", None, [])
    
    def chunk_document(self, doc: DocumentInfo) -> List[ChunkMetadata]:
        """Chunk document into semantic chunks."""
        chunks = []
        current_chunk_paras = []
        current_chunk_type = "mixed"
        current_article = None
        current_paragraph_nums = []
        char_offset = 0
        
        # Extract metadata from first paragraph
        regulation_name = MetadataExtractor.extract_regulation_name(doc.paragraphs[0])
        year = MetadataExtractor.extract_year(doc.paragraphs[0])
        doc_type = MetadataExtractor.extract_doc_type(doc.paragraphs[0])
        regulation_refs = MetadataExtractor.extract_regulation_refs(doc.full_text)
        
        for para in doc.paragraphs:
            para_type, article_num, para_nums = self.detect_boundary(para)
            para_tokens = self.count_tokens(para)
            
            # Check if we should start a new chunk
            should_split = False
            
            if current_chunk_paras:
                current_tokens = self.count_tokens("\n".join(current_chunk_paras))
                
                # Split if we detect a new boundary and current chunk is reasonable size
                if para_type in ["article", "section"] and current_tokens >= self.min_chunk_tokens:
                    should_split = True
                
                # Split if we exceed max tokens
                elif current_tokens + para_tokens > self.max_chunk_tokens:
                    should_split = True
                
                # Or if we've reached target and hit any boundary
                elif current_tokens >= self.chunk_target_tokens and para_type in ["article", "recital", "section"]:
                    should_split = True
            
            if should_split:
                # Save current chunk
                chunk_text = "\n".join(current_chunk_paras)
                chunks.append(self._create_chunk_metadata(
                    doc=doc,
                    chunk_id=len(chunks),
                    chunk_text=chunk_text,
                    chunk_type=current_chunk_type,
                    article_number=current_article,
                    paragraph_numbers=current_paragraph_nums,
                    char_start=char_offset,
                    regulation_name=regulation_name,
                    year=year,
                    doc_type=doc_type,
                    regulation_refs=regulation_refs
                ))
                
                char_offset += len(chunk_text) + 1  # +1 for newline
                
                # Reset
                current_chunk_paras = []
                current_paragraph_nums = []
            
            # Add paragraph to current chunk
            current_chunk_paras.append(para)
            
            # Update tracking
            if para_type == "article" and article_num:
                current_article = article_num
                current_chunk_type = "article"
            elif para_type == "recital":
                current_chunk_type = "recital"
                if para_nums:
                    current_paragraph_nums.extend(para_nums)
            elif para_type == "section":
                current_chunk_type = "section"
        
        # Add final chunk
        if current_chunk_paras:
            chunk_text = "\n".join(current_chunk_paras)
            
            # Handle orphans
            if self.merge_orphans and chunks and self.count_tokens(chunk_text) < self.orphan_threshold:
                # Merge with previous chunk
                prev_chunk = chunks[-1]
                merged_text = prev_chunk.full_text + "\n" + chunk_text
                prev_chunk.full_text = merged_text
                prev_chunk.char_end = char_offset + len(chunk_text)
                prev_chunk.token_count = self.count_tokens(merged_text)
                if current_paragraph_nums:
                    prev_chunk.paragraph_numbers.extend(current_paragraph_nums)
            else:
                chunks.append(self._create_chunk_metadata(
                    doc=doc,
                    chunk_id=len(chunks),
                    chunk_text=chunk_text,
                    chunk_type=current_chunk_type,
                    article_number=current_article,
                    paragraph_numbers=current_paragraph_nums,
                    char_start=char_offset,
                    regulation_name=regulation_name,
                    year=year,
                    doc_type=doc_type,
                    regulation_refs=regulation_refs
                ))
        
        return chunks
    
    def _create_chunk_metadata(
        self,
        doc: DocumentInfo,
        chunk_id: int,
        chunk_text: str,
        chunk_type: str,
        article_number: Optional[str],
        paragraph_numbers: List[str],
        char_start: int,
        regulation_name: str,
        year: Optional[int],
        doc_type: str,
        regulation_refs: List[str]
    ) -> ChunkMetadata:
        """Create chunk metadata object."""
        return ChunkMetadata(
            document_id=doc.document_id,
            filename=doc.filename,
            regulation_name=regulation_name,
            year=year,
            doc_type=doc_type,
            chunk_id=chunk_id,
            chunk_type=chunk_type,
            article_number=article_number,
            paragraph_numbers=paragraph_numbers,
            full_text=chunk_text,
            char_start=char_start,
            char_end=char_start + len(chunk_text),
            token_count=self.count_tokens(chunk_text),
            regulation_refs=regulation_refs
        )


# ============================================================================
# GCS Uploader
# ============================================================================

class GCSUploader:
    """Uploads processed chunks to Google Cloud Storage."""
    
    def __init__(self, project_id: str, bucket_name: str, output_prefix: str):
        self.client = storage.Client(project=project_id)
        self.bucket = self.client.bucket(bucket_name)
        self.output_prefix = output_prefix
        self.logger = logging.getLogger(__name__)
    
    def upload_chunks(self, chunks: List[ChunkMetadata], batch_size: int = 1000):
        """Upload chunks as JSONL files in batches."""
        self.logger.info(f"Uploading {len(chunks)} chunks to GCS...")
        
        # Group into batches
        for batch_idx in range(0, len(chunks), batch_size):
            batch = chunks[batch_idx:batch_idx + batch_size]
            
            # Create JSONL content
            jsonl_lines = []
            for chunk in batch:
                jsonl_lines.append(json.dumps(asdict(chunk), ensure_ascii=False))
            
            jsonl_content = "\n".join(jsonl_lines)
            
            # Upload to GCS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"{self.output_prefix}/chunks_batch_{batch_idx:06d}_{timestamp}.jsonl"
            blob = self.bucket.blob(blob_name)
            
            blob.upload_from_string(jsonl_content, content_type='application/jsonl')
            self.logger.info(f"Uploaded batch {batch_idx // batch_size + 1}: {blob_name}")
        
        self.logger.info(f"Upload complete: {len(chunks)} chunks uploaded")


# ============================================================================
# Main Pipeline
# ============================================================================

class PreprocessingPipeline:
    """Main preprocessing pipeline orchestrator."""
    
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self._setup_logging()
        
        self.scanner = DocumentScanner(
            base_path=self.config.get('processing', 'input_directory'),
            exclude_patterns=self.config.get('processing', 'exclude_patterns')
        )
        
        self.chunker = DocumentChunker(self.config)
        
        self.uploader = GCSUploader(
            project_id=self.config.get('gcp', 'project_id'),
            bucket_name=self.config.get('gcp', 'bucket_name'),
            output_prefix=self.config.get('gcp', 'output_prefix')
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging', 'level', default='INFO')
        log_file = self.config.get('logging', 'log_file')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def run(self):
        """Run the full preprocessing pipeline."""
        self.logger.info("=" * 80)
        self.logger.info("EU LEGISLATION PREPROCESSING PIPELINE")
        self.logger.info("=" * 80)
        
        # Step 1: Scan for files
        self.logger.info("\n[STEP 1] Scanning for JSON files...")
        file_paths = self.scanner.scan()
        
        if not file_paths:
            self.logger.error("No files found to process!")
            return
        
        # Step 2: Process documents
        self.logger.info(f"\n[STEP 2] Processing {len(file_paths)} documents...")
        all_chunks = []
        errors = 0
        
        for file_path in tqdm(file_paths, desc="Processing documents"):
            try:
                # Load document
                doc = self.scanner.load_document(file_path)
                if not doc:
                    errors += 1
                    continue
                
                # Chunk document
                chunks = self.chunker.chunk_document(doc)
                all_chunks.extend(chunks)
                
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                errors += 1
        
        self.logger.info(f"\nProcessing complete:")
        self.logger.info(f"  - Documents processed: {len(file_paths) - errors}")
        self.logger.info(f"  - Errors: {errors}")
        self.logger.info(f"  - Total chunks created: {len(all_chunks)}")
        
        # Step 3: Upload to GCS
        self.logger.info(f"\n[STEP 3] Uploading to Google Cloud Storage...")
        batch_size = self.config.get('output', 'batch_size', default=1000)
        self.uploader.upload_chunks(all_chunks, batch_size=batch_size)
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("PIPELINE COMPLETE")
        self.logger.info("=" * 80)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Preprocess EU legislation documents and upload to GCS'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    pipeline = PreprocessingPipeline(args.config)
    pipeline.run()


if __name__ == '__main__':
    main()
