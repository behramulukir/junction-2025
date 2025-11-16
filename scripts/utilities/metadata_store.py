#!/usr/bin/env python3
"""
Simple in-memory metadata store for RAG queries
Loads metadata from processed chunks or test embeddings
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path


class MetadataStore:
    """In-memory metadata store for chunk metadata."""
    
    def __init__(self):
        self.metadata = {}
        
    def load_from_jsonl(self, filepath: str):
        """Load metadata from JSONL file (embeddings format)."""
        print(f"Loading metadata from {filepath}...")
        count = 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                data = json.loads(line)
                chunk_id = data.get('id')
                
                if chunk_id:
                    # Extract metadata from restricts if present
                    metadata = {
                        'id': chunk_id,
                        'full_text': ''  # Will need to load from original chunks
                    }
                    
                    # Parse restricts to get filterable fields
                    if 'restricts' in data:
                        for restrict in data['restricts']:
                            # Handle both string format "key:value" and dict format
                            if isinstance(restrict, str):
                                if ':' in restrict:
                                    key, value = restrict.split(':', 1)
                                    # Convert to proper types
                                    if key == 'year' and value.isdigit():
                                        metadata[key] = int(value)
                                    elif value != 'None' and value != 'Unknown':
                                        metadata[key] = value
                            elif isinstance(restrict, dict):
                                namespace = restrict.get('namespace', '')
                                allow_list = restrict.get('allow', [])
                                if allow_list:
                                    value = allow_list[0]
                                    if namespace == 'year' and value.isdigit():
                                        metadata[namespace] = int(value)
                                    else:
                                        metadata[namespace] = value
                    
                    self.metadata[chunk_id] = metadata
                    count += 1
                    
                    if count % 10000 == 0:
                        print(f"  Loaded {count} metadata entries...")
        
        print(f"✅ Loaded {count} metadata entries")
        return count
    
    def load_from_processed_chunks(self, chunks_dir: str):
        """Load full metadata from processed_chunks directory."""
        print(f"Loading metadata from {chunks_dir}...")
        chunks_path = Path(chunks_dir)
        count = 0
        
        if not chunks_path.exists():
            print(f"⚠️  Directory not found: {chunks_dir}")
            return 0
        
        for jsonl_file in chunks_path.glob("*.jsonl"):
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    chunk = json.loads(line)
                    chunk_id = f"{chunk.get('document_id')}_{chunk.get('chunk_id')}"
                    
                    # Store complete metadata including new fields
                    self.metadata[chunk_id] = {
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
                        # Legacy fields for backward compatibility
                        'chapter': chunk.get('chapter'),
                        'section': chunk.get('section'),
                    }
                    count += 1
                    
                    if count % 10000 == 0:
                        print(f"  Loaded {count} metadata entries...")
        
        print(f"✅ Loaded {count} metadata entries")
        return count
    
    def get(self, chunk_id: str) -> Optional[Dict]:
        """Get metadata for a chunk ID."""
        return self.metadata.get(chunk_id)
    
    def get_batch(self, chunk_ids: list) -> Dict[str, Dict]:
        """Get metadata for multiple chunk IDs."""
        return {
            cid: self.metadata.get(cid, {'id': cid, 'full_text': 'Metadata not available'})
            for cid in chunk_ids
        }
    
    def extract_paragraph(self, chunk_id: str, paragraph_index: int) -> Optional[str]:
        """Extract a specific paragraph from a chunk using paragraph_indices.
        
        Args:
            chunk_id: Chunk identifier
            paragraph_index: 0-based index of paragraph to extract
            
        Returns:
            Paragraph text or None if not found
        """
        metadata = self.get(chunk_id)
        if not metadata:
            return None
        
        paragraph_indices = metadata.get('paragraph_indices', [])
        if not paragraph_indices or paragraph_index >= len(paragraph_indices):
            return None
        
        start, end = paragraph_indices[paragraph_index]
        return metadata['full_text'][start:end]
    
    def extract_all_paragraphs(self, chunk_id: str) -> List[str]:
        """Extract all paragraphs from a chunk.
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            List of paragraph texts
        """
        metadata = self.get(chunk_id)
        if not metadata:
            return []
        
        full_text = metadata.get('full_text', '')
        paragraph_indices = metadata.get('paragraph_indices', [])
        
        if not paragraph_indices:
            # Fallback to full text if no indices
            return [full_text]
        
        return [full_text[start:end] for start, end in paragraph_indices]
    
    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about the metadata store.
        
        Returns:
            Dictionary with statistics
        """
        if not self.metadata:
            return {}
        
        stats = {
            'total_chunks': len(self.metadata),
            'languages': {},
            'source_types': {},
            'chunk_types': {},
            'with_paragraph_indices': 0,
            'total_paragraphs': 0,
        }
        
        for meta in self.metadata.values():
            # Language stats
            lang = meta.get('language', 'unknown')
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            # Source type stats
            src = meta.get('source_type', 'unknown')
            stats['source_types'][src] = stats['source_types'].get(src, 0) + 1
            
            # Chunk type stats
            ctype = meta.get('chunk_type', 'unknown')
            stats['chunk_types'][ctype] = stats['chunk_types'].get(ctype, 0) + 1
            
            # Paragraph indices stats
            para_indices = meta.get('paragraph_indices', [])
            if para_indices:
                stats['with_paragraph_indices'] += 1
                stats['total_paragraphs'] += len(para_indices)
        
        return stats
    
    def __len__(self):
        return len(self.metadata)


# Global instance for easy import
_global_store = None


def get_metadata_store() -> MetadataStore:
    """Get or create global metadata store."""
    global _global_store
    if _global_store is None:
        _global_store = MetadataStore()
    return _global_store


def init_metadata_store(source: str = "test_embeddings", 
                        fallback_sources: Optional[List[str]] = None) -> MetadataStore:
    """Initialize metadata store from various sources with fallback support.
    
    Args:
        source: Primary source (file path or directory name)
        fallback_sources: Optional list of fallback sources to try
        
    Returns:
        MetadataStore instance
    """
    store = get_metadata_store()
    sources_to_try = [source]
    if fallback_sources:
        sources_to_try.extend(fallback_sources)
    
    for src in sources_to_try:
        try:
            # Check if it's a pickle file
            if src.endswith('.pkl'):
                if os.path.exists(src):
                    print(f"Loading metadata from pickle: {src}")
                    import pickle
                    with open(src, 'rb') as f:
                        store.metadata = pickle.load(f)
                    print(f"✅ Loaded {len(store)} entries from pickle")
                    return store
            # Check if it's a JSONL file
            elif src.endswith('.jsonl'):
                if os.path.exists(src):
                    store.load_from_jsonl(src)
                    return store
            # Check if it's a directory
            elif os.path.isdir(src):
                store.load_from_processed_chunks(src)
                return store
            # Legacy string identifiers
            elif src == "test_embeddings":
                if os.path.exists("test_embeddings.jsonl"):
                    store.load_from_jsonl("test_embeddings.jsonl")
                    return store
            elif src == "processed_chunks":
                if os.path.isdir("processed_chunks"):
                    store.load_from_processed_chunks("processed_chunks")
                    return store
        except Exception as e:
            print(f"  Failed to load from {src}: {e}")
            continue
    
    raise ValueError(f"Could not load metadata from any source: {sources_to_try}")


if __name__ == "__main__":
    # Test the metadata store
    import sys
    
    source = sys.argv[1] if len(sys.argv) > 1 else "test_embeddings"
    
    print(f"\n{'='*80}")
    print(f"Testing Metadata Store (source: {source})")
    print(f"{'='*80}\n")
    
    store = init_metadata_store(source)
    
    print(f"\nTotal entries: {len(store)}")
    
    if len(store) > 0:
        # Show statistics
        stats = store.get_statistics()
        print(f"\nStatistics:")
        print(f"  Total chunks: {stats['total_chunks']:,}")
        print(f"  With paragraph indices: {stats['with_paragraph_indices']:,}")
        print(f"  Total paragraphs: {stats['total_paragraphs']:,}")
        print(f"\n  Languages: {dict(stats['languages'])}")
        print(f"  Source types: {dict(stats['source_types'])}")
        print(f"  Chunk types: {dict(stats['chunk_types'])}")
        
        # Show first entry
        first_id = list(store.metadata.keys())[0]
        first_meta = store.get(first_id)
        print(f"\nSample entry ({first_id}):")
        
        # Show key fields
        for key in ['document_id', 'filename', 'regulation_name', 'year', 'chunk_type', 
                    'language', 'source_type', 'token_count']:
            if key in first_meta:
                print(f"  {key}: {first_meta[key]}")
        
        # Show paragraph indices info
        para_indices = first_meta.get('paragraph_indices', [])
        if para_indices:
            print(f"  paragraph_indices: {len(para_indices)} paragraphs")
            print(f"\n  First paragraph:")
            first_para = store.extract_paragraph(first_id, 0)
            if first_para:
                print(f"    '{first_para[:100]}...'")
        
        # Show full text preview
        full_text = first_meta.get('full_text', '')
        if full_text:
            print(f"\n  full_text preview: '{full_text[:150]}...'")
