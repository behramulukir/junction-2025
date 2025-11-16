#!/usr/bin/env python3
"""
Helper script to demonstrate extracting individual paragraphs from chunks using paragraph_indices.

Usage:
    python3 extract_paragraphs.py <chunk_file.jsonl> [chunk_number]
    
Example:
    python3 extract_paragraphs.py test_output/chunks_batch_000000.jsonl 0
"""

import json
import sys
from pathlib import Path


def extract_paragraphs(chunk):
    """Extract individual paragraphs from a chunk using paragraph_indices."""
    full_text = chunk['full_text']
    indices = chunk['paragraph_indices']
    
    paragraphs = []
    for start, end in indices:
        paragraphs.append(full_text[start:end])
    
    return paragraphs


def display_chunk_info(chunk, show_paragraphs=True):
    """Display detailed information about a chunk."""
    print(f"{'='*80}")
    print(f"Chunk ID: {chunk['chunk_id']}")
    print(f"Document: {chunk['document_id']}")
    print(f"Type: {chunk['chunk_type']}")
    print(f"Source: {chunk['source_type']} ({chunk['language']})")
    print(f"Tokens: {chunk['token_count']}")
    print(f"Full text length: {len(chunk['full_text'])} chars")
    print(f"Number of paragraphs: {len(chunk['paragraph_indices'])}")
    
    if chunk['article_number']:
        print(f"Article: {chunk['article_number']}")
    
    if chunk['paragraph_numbers']:
        print(f"Paragraph numbers: {chunk['paragraph_numbers'][:10]}" + 
              (f" ... ({len(chunk['paragraph_numbers'])} total)" if len(chunk['paragraph_numbers']) > 10 else ""))
    
    print()
    
    if show_paragraphs:
        paragraphs = extract_paragraphs(chunk)
        print(f"Individual Paragraphs ({len(paragraphs)} total):")
        print(f"{'-'*80}")
        
        for i, para in enumerate(paragraphs[:10], 1):  # Show first 10
            start, end = chunk['paragraph_indices'][i-1]
            display_text = para[:100] + '...' if len(para) > 100 else para
            print(f"\nPara {i} [chars {start}-{end}]:")
            print(f"  {display_text}")
        
        if len(paragraphs) > 10:
            print(f"\n... and {len(paragraphs) - 10} more paragraphs")
    
    print(f"{'='*80}\n")


def verify_reconstruction(chunk):
    """Verify that paragraph_indices correctly reconstruct the full_text."""
    full_text = chunk['full_text']
    indices = chunk['paragraph_indices']
    
    # Reconstruct by joining paragraphs with newlines
    reconstructed = '\n'.join([full_text[s:e] for s, e in indices])
    
    if reconstructed == full_text:
        print("✓ Paragraph reconstruction: PASS")
        return True
    else:
        print("✗ Paragraph reconstruction: FAIL")
        print(f"  Original length: {len(full_text)}")
        print(f"  Reconstructed length: {len(reconstructed)}")
        return False


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    chunk_file = Path(sys.argv[1])
    
    if not chunk_file.exists():
        print(f"Error: File not found: {chunk_file}")
        sys.exit(1)
    
    # Read chunks
    with open(chunk_file, 'r', encoding='utf-8') as f:
        chunks = [json.loads(line) for line in f]
    
    print(f"Loaded {len(chunks)} chunks from {chunk_file.name}\n")
    
    # If chunk number specified, show only that chunk
    if len(sys.argv) >= 3:
        chunk_idx = int(sys.argv[2])
        if chunk_idx < 0 or chunk_idx >= len(chunks):
            print(f"Error: Chunk index {chunk_idx} out of range (0-{len(chunks)-1})")
            sys.exit(1)
        
        chunk = chunks[chunk_idx]
        display_chunk_info(chunk, show_paragraphs=True)
        verify_reconstruction(chunk)
    
    else:
        # Show summary of all chunks
        print("Summary of all chunks:")
        print(f"{'='*80}")
        
        for chunk in chunks[:5]:  # Show first 5
            display_chunk_info(chunk, show_paragraphs=False)
        
        if len(chunks) > 5:
            print(f"... and {len(chunks) - 5} more chunks\n")
        
        # Verify all reconstructions
        print("\nVerifying paragraph reconstruction for all chunks:")
        all_pass = True
        for i, chunk in enumerate(chunks):
            if not verify_reconstruction(chunk):
                print(f"  Chunk {i}: FAIL")
                all_pass = False
        
        if all_pass:
            print(f"\n✓ All {len(chunks)} chunks passed reconstruction test!")


if __name__ == '__main__':
    main()
