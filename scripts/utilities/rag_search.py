#!/usr/bin/env python3
"""
RAG query system for EU legislation search
Combines vector search with LLM analysis for finding regulatory overlaps and contradictions
"""

import sys
from pathlib import Path
import os
import pickle

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import vertexai
from vertexai.generative_models import GenerativeModel
from typing import List, Dict, Optional
import json
import argparse
import time
from google.api_core import exceptions as gcp_exceptions
from metadata_store import init_metadata_store, get_metadata_store
from config_loader import get_config


class EULegislationRAG:
    """RAG system for EU legislation semantic search and analysis."""
    
    def __init__(self, 
                 project_id: str,
                 location: str,
                 index_endpoint_name: str,
                 deployed_index_id: str,
                 metadata_file: str = "metadata_store_production.pkl",
                 risk_categories: Optional[Dict] = None):
        """Initialize the RAG system.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            index_endpoint_name: Full resource name of the index endpoint
            deployed_index_id: ID of the deployed index
            metadata_file: Path to metadata pickle file
            risk_categories: Optional risk categories dict (loaded from config if not provided)
        """
        # Load risk categories from config if not provided
        if risk_categories is None:
            config = get_config()
            risk_categories = config.get_rag_config()['risk_categories']
        
        self.risk_categories = risk_categories
        
        aiplatform.init(project=project_id, location=location)
        # Initialize vertexai with us-central1 for Gemini models
        vertexai.init(project=project_id, location="us-central1")
        
        # Use text-multilingual-embedding-002 - Google's best performing model
        # Superior semantic understanding, 2048 token context, excellent for legal/regulatory text
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-multilingual-embedding-002")
        
        # Try available Gemini models in order of preference
        available_models = ["gemini-2.5-pro"]
        self.chat_model = None
        for model_name in available_models:
            try:
                self.chat_model = GenerativeModel(model_name)
                print(f"  Using Gemini model: {model_name}")
                break
            except Exception as e:
                continue
        
        if not self.chat_model:
            print("  WARNING: No Gemini model available, LLM analysis will be skipped")
        
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name)
        self.deployed_index_id = deployed_index_id
        
        # Initialize metadata store - load production metadata from pickle
        import pickle
        import os
        
        if os.path.exists(metadata_file):
            print(f"  Loading production metadata from {metadata_file}...")
            with open(metadata_file, 'rb') as f:
                self.metadata_store = pickle.load(f)
        else:
            print(f"  ERROR: {metadata_file} not found!")
            print(f"  Run: python build_metadata_store.py to create {metadata_file}")
            self.metadata_store = {}
        
        print(f"Initialized EULegislationRAG")
        print(f"  Project: {project_id}")
        print(f"  Endpoint: {index_endpoint_name}")
        print(f"  Deployed Index: {deployed_index_id}")
        print(f"  Metadata entries: {len(self.metadata_store)}")
    
    def _get_embeddings_with_retry(self, texts: List[str], max_retries: int = 5) -> List:
        """Get embeddings with exponential backoff retry on quota errors.
        
        Args:
            texts: List of texts to embed
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of embedding values
        """
        for attempt in range(max_retries):
            try:
                return self.embedding_model.get_embeddings(texts)
            except gcp_exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) + (attempt * 0.5)  # Exponential backoff
                print(f"  Quota exceeded, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            except Exception as e:
                # Don't retry on other errors
                raise
        raise Exception("Failed to get embeddings after retries")
    
    def _expand_query(self, query: str, num_variations: int = 2) -> List[str]:
        """Generate query variations using Gemini for better recall.
        
        Args:
            query: Original user query
            num_variations: Number of variations to generate (0 to disable)
            
        Returns:
            List of query variations
        """
        if num_variations <= 0:
            return []
        
        prompt = f"""Generate {num_variations} alternative phrasings of the following search query for EU legislation.
Keep the core intent but vary the wording, terminology, and perspective.
Focus on regulatory and legal terminology variations.

Original query: {query}

Provide ONLY the alternative queries, one per line, without numbering or explanation."""
        
        try:
            response = self.chat_model.generate_content(prompt)
            variations = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            return variations[:num_variations]
        except Exception as e:
            print(f"  Query expansion failed: {e}")
            return []
    
    def query(self, 
              user_query: str, 
              risk_category: Optional[str] = None,
              year_filter: Optional[int] = None,
              language_filter: Optional[str] = None,
              source_type_filter: Optional[str] = None,
              top_k: int = 50,
              llm_top_k: Optional[int] = None,
              analyze_with_llm: bool = True,
              focus_cross_regulation: bool = True,
              use_query_expansion: bool = True,
              query_variations: int = 2,
              use_paragraph_context: bool = True,
              discard_unknown_metadata: bool = False) -> Dict:
        """Execute a search query and optionally analyze results with LLM.
        
        Args:
            user_query: Natural language query
            risk_category: Optional risk category filter
            year_filter: Optional minimum year filter (e.g., 2016)
            language_filter: Optional language filter (e.g., 'en', 'fi', 'multi')
            source_type_filter: Optional source type filter (e.g., 'eu_legislation', 'national_law', 'international_standard')
            top_k: Number of similar chunks to retrieve from vector search
            llm_top_k: Number of unique chunks to pass to LLM (if None, uses top_k)
            analyze_with_llm: Whether to analyze results with Gemini
            focus_cross_regulation: If True, only report contradictions/overlaps between different regulations, not within same regulation
            use_query_expansion: If True, generate query variations for better recall
            query_variations: Number of query variations to generate (0 to disable expansion)
            use_paragraph_context: If True, extract key paragraphs for better LLM context
            discard_unknown_metadata: If True, filter out chunks with 'Metadata not available' before passing to LLM
        
        Returns:
            Dict with search results and optional LLM analysis
        """
        print(f"\n{'='*80}")
        print(f"QUERY: {user_query}")
        print(f"{'='*80}")
        
        # Step 1: Query expansion (optional)
        queries_to_search = [user_query]
        if use_query_expansion and query_variations > 0:
            print(f"Generating {query_variations} query variations for better recall...")
            expanded_queries = self._expand_query(user_query, query_variations)
            queries_to_search.extend(expanded_queries)
            print(f"  Generated {len(expanded_queries)} variations")
        
        # Step 2: Vectorize queries
        print(f"Generating embeddings for {len(queries_to_search)} queries...")
        query_embeddings = [emb.values for emb in self._get_embeddings_with_retry(queries_to_search)]
        
        # Step 3: Vector search for all query variations
        all_results = {}
        for i, query_embedding in enumerate(query_embeddings):
            search_results = self.index_endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=top_k if not use_query_expansion else 30
            )
            
            # Collect results with their rank
            for rank, neighbor in enumerate(search_results[0]):
                if neighbor.id not in all_results:
                    all_results[neighbor.id] = {
                        'neighbor': neighbor,
                        'ranks': [],
                        'best_score': float(neighbor.distance)
                    }
                all_results[neighbor.id]['ranks'].append(rank + 1)
                all_results[neighbor.id]['best_score'] = max(
                    all_results[neighbor.id]['best_score'],
                    float(neighbor.distance)
                )
        
        # Apply Reciprocal Rank Fusion (RRF) if using query expansion
        if use_query_expansion and len(queries_to_search) > 1:
            print(f"Fusing results from {len(queries_to_search)} queries using RRF...")
            for result_id, result_data in all_results.items():
                # RRF score: sum of 1/(k + rank) for each appearance
                rrf_score = sum(1.0 / (60 + rank) for rank in result_data['ranks'])
                result_data['rrf_score'] = rrf_score
            
            # Sort by RRF score (higher is better)
            sorted_ids = sorted(all_results.keys(), 
                              key=lambda x: all_results[x]['rrf_score'], 
                              reverse=True)[:top_k]
        else:
            # Sort by distance score (higher is better for dot product)
            sorted_ids = sorted(all_results.keys(), 
                              key=lambda x: all_results[x]['best_score'], 
                              reverse=True)[:top_k]
        
        # Reconstruct neighbor-like results from sorted IDs
        print(f"Retrieved {len(all_results)} unique results, using top {len(sorted_ids)}...")
        
        # Extract neighbor IDs and fetch metadata from store
        neighbor_ids = sorted_ids
        
        # Process results with metadata
        chunks = []
        for neighbor_id in neighbor_ids:
            result_data = all_results[neighbor_id]
            neighbor = result_data['neighbor']
            
            # Get metadata from dictionary
            metadata = self.metadata_store.get(neighbor_id, {
                'id': neighbor_id,
                'full_text': 'Metadata not available'
            })
            
            # Apply filters
            if year_filter and metadata.get('year', 0) and metadata['year'] < year_filter:
                continue
            
            if risk_category and not self._matches_risk_category(metadata, risk_category):
                continue
            
            if language_filter and metadata.get('language') != language_filter:
                continue
            
            if source_type_filter and metadata.get('source_type') != source_type_filter:
                continue
            
            # Use RRF score if available, otherwise use distance
            score = result_data.get('rrf_score', float(neighbor.distance))
            
            chunks.append({
                'score': score,
                'id': neighbor_id,
                'metadata': metadata
            })
        
        print(f"Found {len(chunks)} relevant chunks after filtering")
        
        # Step 3: Filter for LLM (optional)
        llm_chunks = chunks
        if discard_unknown_metadata:
            original_count = len(llm_chunks)
            llm_chunks = [c for c in llm_chunks if c['metadata'].get('full_text') != 'Metadata not available']
            print(f"Filtered out {original_count - len(llm_chunks)} chunks with unknown metadata")
        
        # Determine how many chunks to pass to LLM
        effective_llm_top_k = llm_top_k if llm_top_k is not None else min(30, len(llm_chunks))
        
        # Step 4: LLM Analysis (optional)
        analysis = None
        if analyze_with_llm and llm_chunks:
            print(f"Analyzing with Gemini LLM (using top {effective_llm_top_k} chunks)...")
            analysis = self._analyze_with_llm(user_query, llm_chunks[:effective_llm_top_k], focus_cross_regulation)
        
        result = {
            'query': user_query,
            'filters': {
                'risk_category': risk_category,
                'year_filter': year_filter,
                'language_filter': language_filter,
                'source_type_filter': source_type_filter
            },
            'num_results': len(chunks),
            'top_chunks': chunks[:10],
            'llm_analysis': analysis,
            'use_paragraph_context': use_paragraph_context
        }
        
        return result
    
    def _matches_risk_category(self, metadata: Dict, category: str) -> bool:
        """Check if chunk matches risk category keywords.
        
        Args:
            metadata: Chunk metadata
            category: Risk category name
            
        Returns:
            bool: True if matches
        """
        if category not in self.risk_categories:
            return True
        
        keywords = self.risk_categories[category]
        text = metadata.get('full_text', '').lower()
        reg_name = metadata.get('regulation_name', '').lower()
        
        return any(kw.lower() in text or kw.lower() in reg_name for kw in keywords)
    
    def _analyze_with_llm(self, query: str, chunks: List[Dict], focus_cross_regulation: bool = True) -> str:
        """Use Gemini to analyze retrieved chunks for overlaps and contradictions.
        
        Args:
            query: User query
            chunks: Retrieved chunks with metadata
            focus_cross_regulation: If True, only analyze contradictions/overlaps between different regulations
            
        Returns:
            str: LLM analysis
        """
        # Build context from chunks
        context = self._format_chunks_for_llm(chunks)
        
        # Build analysis instructions based on focus_cross_regulation
        if focus_cross_regulation:
            analysis_scope = """IMPORTANT: Focus ONLY on contradictions and overlaps BETWEEN DIFFERENT regulations. 
Do NOT report contradictions or overlaps between articles within the SAME regulation, as these are typically intentional complementary provisions.
Only flag issues where provisions from DIFFERENT regulations conflict or overlap."""
            contradiction_instruction = "Identify contradictions ONLY between DIFFERENT regulations (not within the same regulation)"
            overlap_instruction = "Find overlapping regulatory scope ONLY between DIFFERENT regulations (not within the same regulation)"
        else:
            analysis_scope = ""
            contradiction_instruction = "Identify any direct contradictions between articles/regulations"
            overlap_instruction = "Find overlapping regulatory scope or requirements"
        
        prompt = f"""You are a regulatory compliance analyst specializing in multi-jurisdictional regulatory analysis for financial institutions.

TASK: Analyze the following regulations for overlaps, contradictions, and relationships relevant to the query.
Consider EU legislation, national laws, and international standards together.

{analysis_scope}

USER QUERY: {query}

RELEVANT REGULATIONS:
{context}

ANALYSIS INSTRUCTIONS:
1. {contradiction_instruction}
2. {overlap_instruction}
3. Highlight ambiguous areas requiring legal interpretation
4. Note complementary relationships between regulations across jurisdictions
5. Consider cross-references and dependencies between regulations
6. Pay attention to source types (EU vs. National vs. International standards)
7. Consider implications for financial institutions and banking sector

For each finding, provide:
- Regulation name + Article/Paragraph citation + Source Type
- Exact relevant text (brief quote)
- Explanation of overlap/contradiction/relationship
- Cross-references to other regulations (if applicable)
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Practical impact for compliance

OUTPUT FORMAT: 
Use clear sections with headings:
- SUMMARY (include source type distribution)
- KEY FINDINGS (numbered list with source types)
- CONTRADICTIONS (if any) - specify if cross-jurisdictional
- OVERLAPS (if any) - note EU/national/international relationships
- CROSS-REFERENCES (explicit regulation references found)
- RECOMMENDATIONS (consider multi-jurisdictional compliance)

Be precise and cite specific articles with source types. Focus on actionable insights.
"""
        
        try:
            response = self.chat_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"LLM analysis failed: {str(e)}"
    
    def _format_chunks_for_llm(self, chunks: List[Dict]) -> str:
        """Format chunks with citations for LLM context.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            str: Formatted context
        """
        formatted = []
        
        for i, chunk in enumerate(chunks, 1):
            meta = chunk['metadata']
            
            # Build citation
            citation_parts = []
            if meta.get('regulation_name'):
                citation_parts.append(meta['regulation_name'])
            if meta.get('article_number'):
                citation_parts.append(f"Article {meta['article_number']}")
            if meta.get('paragraph_numbers') and meta['paragraph_numbers']:
                citation_parts.append(f"Paras {', '.join(str(p) for p in meta['paragraph_numbers'][:3])}")
            
            citation = " | ".join(citation_parts) if citation_parts else "Unknown Source"
            
            # Extract key paragraphs if paragraph_indices available
            text = meta.get('full_text', 'No text available')
            paragraph_info = ""
            
            if meta.get('paragraph_indices') and len(meta['paragraph_indices']) > 1:
                # Use first 2-3 paragraphs for focused context
                full_text = meta['full_text']
                key_paragraphs = []
                for start, end in meta['paragraph_indices'][:3]:
                    para = full_text[start:end]
                    if len(para) > 20:  # Skip very short paragraphs
                        key_paragraphs.append(para)
                
                if key_paragraphs:
                    text = "\n\n".join(key_paragraphs)
                    paragraph_info = f" [{len(meta['paragraph_indices'])} paragraphs, showing first {len(key_paragraphs)}]"
            
            # Limit text length for context window
            if len(text) > 800:
                text = text[:800] + "..."
            
            # Build metadata line with new fields
            metadata_parts = [
                f"Year: {meta.get('year', 'N/A')}",
                f"Type: {meta.get('doc_type', 'Unknown')}",
                f"Source: {meta.get('source_type', 'unknown')}",
                f"Lang: {meta.get('language', 'en')}",
                f"Chunk: {meta.get('chunk_type', 'unknown')}"
            ]
            
            # Add regulation references if available
            reg_refs = meta.get('regulation_refs', [])
            if reg_refs:
                metadata_parts.append(f"Refs: {', '.join(reg_refs[:3])}{'...' if len(reg_refs) > 3 else ''}")
            
            formatted.append(f"""
[CHUNK {i}] {citation}{paragraph_info}
{' | '.join(metadata_parts)}
Similarity: {chunk['score']:.3f}

{text}
{'─' * 80}
""")
        
        return "\n".join(formatted)
    
    def print_results(self, result: Dict):
        """Print formatted search results.
        
        Args:
            result: Query result dictionary
        """
        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS")
        print(f"{'='*80}")
        print(f"Query: {result['query']}")
        
        # Show active filters
        filters = result['filters']
        active_filters = []
        if filters.get('risk_category'):
            active_filters.append(f"Risk: {filters['risk_category']}")
        if filters.get('year_filter'):
            active_filters.append(f"Year >= {filters['year_filter']}")
        if filters.get('language_filter'):
            active_filters.append(f"Lang: {filters['language_filter']}")
        if filters.get('source_type_filter'):
            active_filters.append(f"Source: {filters['source_type_filter']}")
        
        if active_filters:
            print(f"Filters: {' | '.join(active_filters)}")
        
        print(f"Total Results: {result['num_results']}")
        
        print(f"\n{'─'*80}")
        print(f"TOP 5 MATCHES:")
        print(f"{'─'*80}")
        
        for i, chunk in enumerate(result['top_chunks'][:5], 1):
            meta = chunk['metadata']
            print(f"\n{i}. {meta.get('regulation_name', 'Unknown')}")
            
            # First line: Article, Year, Score
            info_parts = [
                f"Article: {meta.get('article_number', 'N/A')}",
                f"Year: {meta.get('year', 'N/A')}",
                f"Score: {chunk['score']:.3f}"
            ]
            print(f"   {' | '.join(info_parts)}")
            
            # Second line: Source, Language, Chunk Type
            meta_parts = [
                f"Source: {meta.get('source_type', 'unknown')}",
                f"Lang: {meta.get('language', 'en')}",
                f"Type: {meta.get('chunk_type', 'unknown')}"
            ]
            
            # Add paragraph count if available
            if meta.get('paragraph_indices'):
                meta_parts.append(f"Paragraphs: {len(meta['paragraph_indices'])}")
            
            print(f"   {' | '.join(meta_parts)}")
            
            # Show regulation references if available
            reg_refs = meta.get('regulation_refs', [])
            if reg_refs:
                print(f"   Cross-refs: {', '.join(reg_refs[:3])}{'...' if len(reg_refs) > 3 else ''}")
            
            # Show text preview
            print(f"   Text: {meta.get('full_text', '')[:150]}...")
        
        if result['llm_analysis']:
            print(f"\n{'='*80}")
            print(f"LLM ANALYSIS")
            print(f"{'='*80}")
            print(result['llm_analysis'])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Query EU legislation using RAG system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Support:
  Set APP_ENV environment variable to switch configurations:
    export APP_ENV=development   # Use dev config
    export APP_ENV=staging       # Use staging config  
    export APP_ENV=production    # Use production config (default)

Examples:
  # Query with default settings
  python rag_search.py --index-endpoint <endpoint> --query "GDPR data protection"
  
  # With filters
  python rag_search.py --index-endpoint <endpoint> --query "Banking regulation" \\
    --risk-category financial_regulation --year-filter 2018
  
  # Fast mode (no LLM, no query expansion)
  python rag_search.py --index-endpoint <endpoint> --query "MiFID II" \\
    --no-llm --no-query-expansion
        """
    )
    parser.add_argument(
        '--env',
        type=str,
        choices=['development', 'staging', 'production'],
        help='Environment (overrides APP_ENV variable)'
    )
    parser.add_argument(
        '--project-id',
        type=str,
        help='GCP project ID (overrides config)'
    )
    parser.add_argument(
        '--location',
        type=str,
        help='GCP region (overrides config)'
    )
    parser.add_argument(
        '--index-endpoint',
        type=str,
        required=True,
        help='Full resource name of index endpoint (from build_vector_index.py output)'
    )
    parser.add_argument(
        '--deployed-index-id',
        type=str,
        help='Deployed index ID (overrides config, default: eu_legislation_deployed)'
    )
    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='Search query'
    )
    parser.add_argument(
        '--risk-category',
        type=str,
        help='Filter by risk category (loaded from config)'
    )
    parser.add_argument(
        '--year-filter',
        type=int,
        help='Minimum year filter (e.g., 2016)'
    )
    parser.add_argument(
        '--language',
        type=str,
        choices=['en', 'fi', 'multi'],
        help='Filter by language (en=English, fi=Finnish, multi=multilingual)'
    )
    parser.add_argument(
        '--source-type',
        type=str,
        choices=['eu_legislation', 'national_law', 'international_standard'],
        help='Filter by source type'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        help='Number of results to retrieve from vector search (default from config)'
    )
    parser.add_argument(
        '--llm-top-k',
        type=int,
        help='Number of unique chunks to pass to LLM for analysis (default: min(30, top_k))'
    )
    parser.add_argument(
        '--use-paragraphs',
        action='store_true',
        help='Extract key paragraphs for better LLM context (uses paragraph_indices)'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM analysis'
    )
    parser.add_argument(
        '--focus-cross-regulation',
        action='store_true',
        default=True,
        help='Only report contradictions/overlaps between different regulations (default: True)'
    )
    parser.add_argument(
        '--include-same-regulation',
        action='store_true',
        help='Include contradictions/overlaps within the same regulation (overrides --focus-cross-regulation)'
    )
    parser.add_argument(
        '--discard-unknown-metadata',
        action='store_true',
        help='Filter out chunks with unknown metadata before passing to LLM'
    )
    parser.add_argument(
        '--query-variations',
        type=int,
        default=2,
        help='Number of query variations to generate (default: 2, set to 0 to disable query expansion)'
    )
    parser.add_argument(
        '--no-query-expansion',
        action='store_true',
        help='Disable query expansion (faster but lower recall)'
    )
    parser.add_argument(
        '--metadata-file',
        type=str,
        help='Path to metadata pickle file (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config(environment=args.env)
    rag_config = config.get_rag_config()
    
    # Apply CLI overrides
    project_id = args.project_id or rag_config['project_id']
    location = args.location or rag_config['location']
    deployed_index_id = args.deployed_index_id or 'eu_legislation_deployed'
    metadata_file = args.metadata_file or rag_config['metadata_source']
    top_k = args.top_k or rag_config['search']['default_top_k']
    
    # Validate risk category if provided
    risk_categories = rag_config['risk_categories']
    if args.risk_category and args.risk_category not in risk_categories:
        print(f"ERROR: Unknown risk category '{args.risk_category}'")
        print(f"Available categories: {', '.join(risk_categories.keys())}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"RAG System Configuration")
    print(f"{'='*80}")
    print(f"Environment: {config.environment}")
    print(f"Project ID: {project_id}")
    print(f"Embedding Model: {rag_config['embedding_model']}")
    print(f"LLM Model: {rag_config['llm_model']}")
    print(f"Metadata Source: {metadata_file}")
    print(f"{'='*80}\n")
    
    # Initialize RAG system
    rag = EULegislationRAG(
        project_id=project_id,
        location=location,
        index_endpoint_name=args.index_endpoint,
        deployed_index_id=deployed_index_id,
        metadata_file=metadata_file,
        risk_categories=risk_categories
    )
    
    # Determine focus_cross_regulation setting
    focus_cross_regulation = args.focus_cross_regulation and not args.include_same_regulation
    
    # Determine query variations setting (--no-query-expansion overrides --query-variations)
    query_variations = 0 if args.no_query_expansion else args.query_variations
    
    # Execute query
    result = rag.query(
        user_query=args.query,
        risk_category=args.risk_category,
        year_filter=args.year_filter,
        language_filter=args.language,
        source_type_filter=args.source_type,
        top_k=top_k,
        llm_top_k=args.llm_top_k,
        analyze_with_llm=not args.no_llm,
        focus_cross_regulation=focus_cross_regulation,
        use_query_expansion=not args.no_query_expansion,
        query_variations=query_variations,
        use_paragraph_context=args.use_paragraphs,
        discard_unknown_metadata=args.discard_unknown_metadata
    )
    
    # Print results
    rag.print_results(result)


if __name__ == "__main__":
    main()
