#!/usr/bin/env python3
"""
Test preprocessing pipeline on a small subset of files
"""

import json
import logging
from pathlib import Path
from preprocess_local import (
    Config, DocumentScanner, DocumentChunker, 
    MetadataExtractor, LocalFileWriter
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_subset():
    """Test on a small subset of files from each source."""
    
    logger.info("=" * 80)
    logger.info("TESTING PREPROCESSING PIPELINE ON SUBSET")
    logger.info("=" * 80)
    
    # Load config
    config = Config('config.yaml')
    
    # Test files (one from each source)
    test_files = [
        # Finnish national law
        Path("other_national_laws/444_2017.di.json"),
        
        # International standard
        Path("other_regulation_standards/BRRD/CELEX_32014L0059_EN_TXT.di.json"),
        
        # EU legislation (pick one from output folder)
        Path("output/0a0ad2cc-684b-11ec-9136-01aa75ed71a1/fmx4/L_2021465EN.01000101.doc.json"),
    ]
    
    # Filter to only existing files
    test_files = [f for f in test_files if f.exists()]
    
    if not test_files:
        logger.error("No test files found!")
        return
    
    logger.info(f"\nTesting {len(test_files)} files:\n")
    
    # Initialize components
    chunker = DocumentChunker(config)
    writer = LocalFileWriter("test_output")
    
    all_chunks = []
    stats = {
        'eu_legislation': 0,
        'national_law': 0, 
        'international_standard': 0,
        'languages': {'en': 0, 'fi': 0, 'multi': 0}
    }
    
    for file_path in test_files:
        logger.info(f"Processing: {file_path.name}")
        
        # Create appropriate scanner for this file
        if 'other_national_laws' in str(file_path):
            scanner = DocumentScanner('other_national_laws', config.get('processing', 'exclude_patterns'))
        elif 'other_regulation_standards' in str(file_path):
            scanner = DocumentScanner('other_regulation_standards', config.get('processing', 'exclude_patterns'))
        else:
            scanner = DocumentScanner('output', config.get('processing', 'exclude_patterns'))
        
        # Load document
        doc = scanner.load_document(file_path)
        if not doc:
            logger.warning(f"  Failed to load {file_path}")
            continue
        
        # Display document info
        logger.info(f"  Document ID: {doc.document_id}")
        logger.info(f"  Source Type: {doc.source_type}")
        logger.info(f"  Language: {doc.language}")
        logger.info(f"  Paragraphs: {len(doc.paragraphs)}")
        
        # Update stats
        stats[doc.source_type] = stats.get(doc.source_type, 0) + 1
        stats['languages'][doc.language] = stats['languages'].get(doc.language, 0) + 1
        
        # Extract metadata
        first_para = doc.paragraphs[0] if doc.paragraphs else ""
        reg_name = MetadataExtractor.extract_regulation_name(first_para, doc.source_type)
        year = MetadataExtractor.extract_year(first_para)
        doc_type = MetadataExtractor.extract_doc_type(first_para, doc.source_type)
        
        logger.info(f"  Regulation: {reg_name[:80]}...")
        logger.info(f"  Year: {year}")
        logger.info(f"  Doc Type: {doc_type}")
        
        # Chunk document
        try:
            chunks = chunker.chunk_document(doc)
            logger.info(f"  Chunks created: {len(chunks)}")
            
            # Show first chunk details
            if chunks:
                first_chunk = chunks[0]
                logger.info(f"  First chunk:")
                logger.info(f"    - Type: {first_chunk.chunk_type}")
                logger.info(f"    - Tokens: {first_chunk.token_count}")
                logger.info(f"    - Language: {first_chunk.language}")
                logger.info(f"    - Source: {first_chunk.source_type}")
                logger.info(f"    - Text preview: {first_chunk.full_text[:100]}...")
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            logger.error(f"  Chunking failed: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("")
    
    # Write test output
    logger.info(f"\n{'=' * 80}")
    logger.info("SUMMARY")
    logger.info(f"{'=' * 80}")
    logger.info(f"Total chunks created: {len(all_chunks)}")
    logger.info(f"\nSource Type Distribution:")
    for source_type, count in stats.items():
        if source_type != 'languages' and count > 0:
            logger.info(f"  - {source_type}: {count} documents")
    
    logger.info(f"\nLanguage Distribution:")
    for lang, count in stats['languages'].items():
        if count > 0:
            lang_name = {'en': 'English', 'fi': 'Finnish', 'multi': 'Multilingual'}.get(lang, lang)
            logger.info(f"  - {lang_name}: {count} documents")
    
    if all_chunks:
        logger.info(f"\nWriting test output...")
        written_files = writer.write_chunks(all_chunks, batch_size=100)
        logger.info(f"Written to: {written_files}")
        
        # Show sample chunk as JSON
        logger.info(f"\nSample chunk (as JSON):")
        sample = all_chunks[0]
        print(json.dumps({
            'document_id': sample.document_id,
            'filename': sample.filename,
            'regulation_name': sample.regulation_name,
            'year': sample.year,
            'doc_type': sample.doc_type,
            'chunk_type': sample.chunk_type,
            'language': sample.language,
            'source_type': sample.source_type,
            'token_count': sample.token_count,
            'text_preview': sample.full_text[:200]
        }, indent=2))
    
    logger.info(f"\n{'=' * 80}")
    logger.info("TEST COMPLETE")
    logger.info(f"{'=' * 80}")

if __name__ == '__main__':
    test_subset()
