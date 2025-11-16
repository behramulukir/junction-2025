#!/usr/bin/env python3
"""
Comprehensive test of preprocessing improvements across all document types.
Tests national laws, international standards, and EU legislation.
"""

import json
import logging
from pathlib import Path
from preprocess_local import DocumentScanner, DocumentChunker, Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Test files from each category
TEST_FILES = {
    'national_laws': [
        'other_national_laws/444_2017.di.json',  # Anti-Money Laundering
        'other_national_laws/151_2022.di.json',  # Mortgage Credit Banks
        'other_national_laws/38_1978.di.json',   # Older act
    ],
    'international_standards': [
        'other_regulation_standards/BRRD/CELEX_32014L0059_EN_TXT.di.json',  # Bank Recovery
        'other_regulation_standards/CRD/CELEX_32013L0036_EN_TXT.di.json',   # Capital Requirements
        'other_regulation_standards/Basel/BaselFramework.di.json',          # Basel Framework
        'other_regulation_standards/EBA/Final Guidelines on Internal Governance (EBA-GL-2017-11).di.json',
        'other_regulation_standards/IFRS/CELEX_32023R1803_EN_TXT.di.json',  # IFRS
    ],
    'eu_legislation': [
        'output/125480ac-2957-11e6-b616-01aa75ed71a1/fmx4/L_2016147EN.01000101.json',
        'output/547b1f39-9694-11e6-a9e2-01aa75ed71a1/fmx4/L_2016284EN.01002701.json',
        'output/0a4ee661-4433-11e2-9b3b-01aa75ed71a1/fmx4/L_2012343EN.01003201.json',
    ]
}


def test_file(file_path: str, category: str) -> dict:
    """Test preprocessing on a single file."""
    logger = logging.getLogger(__name__)
    
    # Create scanner for this specific file
    scanner = DocumentScanner(
        base_path=str(Path.cwd()),
        exclude_patterns=['*.doc.json', '*.toc.fmx.json']
    )
    
    # Load document
    full_path = Path.cwd() / file_path
    if not full_path.exists():
        return {'error': f'File not found: {file_path}'}
    
    try:
        doc_info = scanner.load_document(full_path)  # Pass Path object, not string
    except Exception as e:
        return {'error': f'Failed to load: {str(e)}'}
    
    # Create chunker
    config = Config('config.yaml')
    chunker = DocumentChunker(config)
    
    # Process chunks
    try:
        chunks = chunker.chunk_document(doc_info)
    except Exception as e:
        return {'error': f'Failed to chunk: {str(e)}'}
    
    # Analyze results
    result = {
        'file': file_path,
        'category': category,
        'document_id': doc_info.document_id,
        'source_type': doc_info.source_type,
        'language': doc_info.language,
        'paragraphs': len(doc_info.paragraphs),
        'chunks_created': len(chunks),
        'first_chunk': None,
        'metadata': {
            'regulation_name': chunks[0].regulation_name if chunks else None,
            'year': chunks[0].year if chunks else None,
            'doc_type': chunks[0].doc_type if chunks else None,
        }
    }
    
    if chunks:
        first_chunk = chunks[0]
        result['first_chunk'] = {
            'chunk_id': first_chunk.chunk_id,
            'chunk_type': first_chunk.chunk_type,
            'article_number': first_chunk.article_number,
            'token_count': first_chunk.token_count,
            'has_document_header': not first_chunk.full_text.startswith(doc_info.paragraphs[0]),
            'text_preview': first_chunk.full_text[:300],
            'paragraph_count': len(first_chunk.paragraph_indices),
        }
    
    return result


def main():
    logger = logging.getLogger(__name__)
    
    print("="*80)
    print("COMPREHENSIVE PREPROCESSING TEST")
    print("="*80)
    print()
    
    results_by_category = {}
    all_results = []
    
    for category, files in TEST_FILES.items():
        print(f"\n{'='*80}")
        print(f"Testing {category.upper().replace('_', ' ')}")
        print(f"{'='*80}\n")
        
        category_results = []
        
        for file_path in files:
            logger.info(f"Testing: {Path(file_path).name}")
            result = test_file(file_path, category)
            category_results.append(result)
            all_results.append(result)
            
            if 'error' in result:
                print(f"  ❌ ERROR: {result['error']}")
                continue
            
            print(f"  ✓ {Path(file_path).name}")
            print(f"    Document ID: {result['document_id']}")
            print(f"    Source Type: {result['source_type']}")
            print(f"    Language: {result['language']}")
            print(f"    Regulation: {result['metadata']['regulation_name'][:60] if result['metadata']['regulation_name'] else 'None'}...")
            print(f"    Year: {result['metadata']['year']}")
            print(f"    Doc Type: {result['metadata']['doc_type']}")
            print(f"    Chunks: {result['chunks_created']}")
            
            if result['first_chunk']:
                fc = result['first_chunk']
                print(f"    First chunk:")
                print(f"      - Type: {fc['chunk_type']}")
                print(f"      - Tokens: {fc['token_count']}")
                print(f"      - Has header: {'✓' if fc['has_document_header'] else '✗'}")
                print(f"      - Paragraphs: {fc['paragraph_count']}")
                print(f"      - Preview: {fc['text_preview'][:80]}...")
            print()
        
        results_by_category[category] = category_results
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_files = len(all_results)
    successful = len([r for r in all_results if 'error' not in r])
    failed = total_files - successful
    
    print(f"\nTotal files tested: {total_files}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    # Metadata quality analysis
    print("\n" + "-"*80)
    print("METADATA QUALITY ANALYSIS")
    print("-"*80)
    
    for category, results in results_by_category.items():
        valid_results = [r for r in results if 'error' not in r]
        if not valid_results:
            continue
        
        print(f"\n{category.upper().replace('_', ' ')}:")
        
        # Check regulation name quality
        good_names = len([r for r in valid_results 
                         if r['metadata']['regulation_name'] 
                         and r['metadata']['regulation_name'] not in ['Unknown', 'N/A']
                         and not r['metadata']['regulation_name'].startswith('1(')])
        
        # Check year extraction
        has_year = len([r for r in valid_results if r['metadata']['year']])
        
        # Check doc type
        has_doc_type = len([r for r in valid_results 
                           if r['metadata']['doc_type'] 
                           and r['metadata']['doc_type'] != 'Unknown'])
        
        # Check document headers
        has_headers = len([r for r in valid_results 
                          if r['first_chunk'] and r['first_chunk']['has_document_header']])
        
        total = len(valid_results)
        print(f"  Regulation names extracted: {good_names}/{total} ({100*good_names/total:.0f}%)")
        print(f"  Years extracted: {has_year}/{total} ({100*has_year/total:.0f}%)")
        print(f"  Doc types extracted: {has_doc_type}/{total} ({100*has_doc_type/total:.0f}%)")
        print(f"  Document headers added: {has_headers}/{total} ({100*has_headers/total:.0f}%)")
    
    # Save detailed results
    output_file = Path('test_comprehensive_results.json')
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n\nDetailed results saved to: {output_file}")
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
