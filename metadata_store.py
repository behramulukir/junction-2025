#!/usr/bin/env python3
"""
Simple in-memory metadata store for RAG queries
Loads metadata from processed chunks or test embeddings
"""

import json
from typing import Dict, Optional
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
                    
                    self.metadata[chunk_id] = {
                        'id': chunk_id,
                        'document_id': chunk.get('document_id'),
                        'chunk_id': chunk.get('chunk_id'),
                        'full_text': chunk.get('full_text', ''),
                        'regulation_name': chunk.get('regulation_name', ''),
                        'year': chunk.get('year'),
                        'doc_type': chunk.get('doc_type', ''),
                        'article_number': chunk.get('article_number'),
                        'paragraph_numbers': chunk.get('paragraph_numbers', []),
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


def init_metadata_store(source: str = "test_embeddings") -> MetadataStore:
    """Initialize metadata store from test embeddings or processed chunks."""
    store = get_metadata_store()
    
    if source == "test_embeddings":
        store.load_from_jsonl("test_embeddings.jsonl")
    elif source == "processed_chunks":
        store.load_from_processed_chunks("processed_chunks")
    else:
        raise ValueError(f"Unknown source: {source}")
    
    return store


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
        # Show first entry
        first_id = list(store.metadata.keys())[0]
        first_meta = store.get(first_id)
        print(f"\nSample entry ({first_id}):")
        print(json.dumps(first_meta, indent=2, ensure_ascii=False)[:500])
