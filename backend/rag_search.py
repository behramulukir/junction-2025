#!/usr/bin/env python3
"""
RAG query system for EU legislation search
Combines vector search with LLM analysis for finding regulatory overlaps and contradictions
"""

from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import vertexai
from vertexai.generative_models import GenerativeModel
from typing import List, Dict, Optional
import json
import argparse
import time
from google.api_core import exceptions as gcp_exceptions

# Configuration
PROJECT_ID = "428461461446"
LOCATION = "europe-west1"
# Production setup
INDEX_ENDPOINT_NAME = "projects/428461461446/locations/europe-west1/indexEndpoints/7728040621125926912"
DEPLOYED_INDEX_ID = "eu_legislation_prod_75480320"


class EULegislationRAG:
    """RAG system for EU legislation semantic search and analysis."""
    
    # Risk categories for Bank of Finland use case
    RISK_CATEGORIES = {
        "data_privacy": ["GDPR", "personal data", "data protection", "privacy", "ePrivacy", "confidentiality"],
        "financial_regulation": ["MiFID", "capital requirements", "banking", "financial stability", "prudential", "Basel"],
        "consumer_protection": ["consumer rights", "unfair terms", "consumer credit", "consumer contracts"],
        "environmental": ["emissions", "waste management", "environmental protection", "climate", "sustainability"],
        "health_safety": ["food safety", "medical devices", "pharmaceuticals", "health", "safety standards"],
        "market_conduct": ["competition", "market abuse", "antitrust", "cartels", "monopoly"],
        "employment": ["working time", "employee rights", "labor conditions", "employment contracts"],
        "telecommunications": ["telecom", "electronic communications", "spectrum", "network"],
        "transport": ["aviation", "maritime", "road transport", "railway", "shipping"],
        "energy": ["energy efficiency", "renewable energy", "electricity", "gas", "energy market"],
        "trade": ["customs", "tariffs", "trade agreements", "import", "export"],
        "taxation": ["tax", "VAT", "excise", "tax evasion", "tax avoidance"],
        "insurance": ["insurance", "reinsurance", "Solvency", "insurance undertaking"],
        "payments": ["payment services", "electronic money", "payment systems", "PSD2"],
        "aml_cft": ["money laundering", "terrorist financing", "AML", "CTF", "suspicious transactions"]
    }
    
    def __init__(self, 
                 project_id: str,
                 location: str,
                 index_endpoint_name: str,
                 deployed_index_id: str,
                 metadata_file: str = "metadata_store_production.pkl"):
        """Initialize the RAG system.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            index_endpoint_name: Full resource name of the index endpoint
            deployed_index_id: ID of the deployed index
            metadata_file: Path to metadata pickle file
        """
        aiplatform.init(project=project_id, location=location)
        # Initialize vertexai with us-central1 for Gemini models
        vertexai.init(project=project_id, location="us-central1")
        
        # Use text-multilingual-embedding-002 - Google's best performing model
        # Superior semantic understanding, 2048 token context, excellent for legal/regulatory text
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
        
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
            num_variations: Number of variations to generate
            
        Returns:
            List of query variations
        """
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
              top_k: int = 50,
              analyze_with_llm: bool = True,
              focus_cross_regulation: bool = True,
              use_query_expansion: bool = True) -> Dict:
        """Execute a search query and optionally analyze results with LLM.
        
        Args:
            user_query: Natural language query
            risk_category: Optional risk category filter
            year_filter: Optional minimum year filter (e.g., 2016)
            top_k: Number of similar chunks to retrieve
            analyze_with_llm: Whether to analyze results with Gemini
            focus_cross_regulation: If True, only report contradictions/overlaps between different regulations, not within same regulation
            use_query_expansion: If True, generate query variations for better recall
        
        Returns:
            Dict with search results and optional LLM analysis
        """
        print(f"\n{'='*80}")
        print(f"QUERY: {user_query}")
        print(f"{'='*80}")
        
        # Step 1: Query expansion (optional)
        queries_to_search = [user_query]
        if use_query_expansion:
            print("Generating query variations for better recall...")
            expanded_queries = self._expand_query(user_query)
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
            
            # Use RRF score if available, otherwise use distance
            score = result_data.get('rrf_score', float(neighbor.distance))
            
            chunks.append({
                'score': score,
                'id': neighbor_id,
                'metadata': metadata
            })
        
        print(f"Found {len(chunks)} relevant chunks after filtering")
        
        # Step 3: LLM Analysis (optional)
        analysis = None
        if analyze_with_llm and chunks:
            print("Analyzing with Gemini LLM...")
            # Use fewer chunks for clearer, more focused analysis
            analysis = self._analyze_with_llm(user_query, chunks[:10], focus_cross_regulation)
        
        result = {
            'query': user_query,
            'filters': {
                'risk_category': risk_category,
                'year_filter': year_filter
            },
            'num_results': len(chunks),
            'top_chunks': chunks,  # Return all chunks, let the API decide how many to use
            'llm_analysis': analysis
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
        if category not in self.RISK_CATEGORIES:
            return True
        
        keywords = self.RISK_CATEGORIES[category]
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
        
        # STEP 1: Analysis prompt - let Gemini analyze freely without format constraints
        analysis_prompt = f"""You are a regulatory compliance analyst. Analyze these EU regulations for overlaps and contradictions.

{analysis_scope}

USER QUERY: {query}

REGULATIONS:
{context}

TASK:
- {contradiction_instruction}
- {overlap_instruction}
- Find at least 2-3 overlaps or contradictions (even minor ones like complementary requirements or overlapping scope)
- Be specific with regulation names and article numbers
- Explain each finding clearly

Write your analysis naturally. Focus on finding the relationships, not on formatting."""

        try:
            # First call: Get free-form analysis
            print("  Step 1: Analyzing regulations (free-form)...")
            response = self.chat_model.generate_content(analysis_prompt)
            raw_analysis = response.text
            print(f"  Raw analysis: {len(raw_analysis)} chars")
            
            # STEP 2: Formatting prompt - convert to strict format
            format_prompt = f"""Your job is to reformat text into a specific structure for computer parsing.

INPUT TEXT:
{raw_analysis}

YOUR TASK: Extract the overlaps, contradictions, and recommendations from the input text and format them EXACTLY as shown below.

REQUIRED OUTPUT FORMAT (copy this structure exactly):

SUMMARY
Write a brief 2-3 sentence summary here.

CONTRADICTIONS
1. Regulation (EU) No 575/2013 Article 124 vs Directive 2013/36/EU Article 73 - Brief description of the contradiction.
2. Regulation (EU) 2019/876 Article 10 vs Directive 2013/36/EU Article 45 - Brief description of the contradiction.

OVERLAPS
1. Regulation (EU) No 575/2013 Article 4 vs Regulation (EU) 2019/876 Article 2 - Brief description of the overlap.
2. Directive 2013/36/EU Article 98 vs Regulation (EU) No 575/2013 Article 376 - Brief description of the overlap.
3. Regulation (EU) No 575/2013 Article 395 vs Directive 2013/36/EU Article 81 - Brief description of the overlap.

RECOMMENDATIONS
1. First recommendation text here.
2. Second recommendation text here.

CRITICAL RULES:
1. Each numbered item MUST be on ONE single line (no line breaks within an item)
2. Format for each item: NUMBER. Regulation Name Article X vs Regulation Name Article Y - Description.
3. Remove ALL bold formatting (remove ** symbols)
4. Remove ALL quotation marks
5. Remove words like "Quote:", "Explanation:", "Severity:", "Practical Impact:"
6. Keep descriptions brief (one sentence per item)
7. If no contradictions found, write: None identified
8. Must have at least 2 overlaps

Start your output with "SUMMARY" and end with the last recommendation. Do not add any other text before or after.

START OUTPUT WITH "SUMMARY" NOW:"""

            # Second call: Get formatted version with strict generation config
            print("  Step 2: Formatting for parser...")
            reformat_response = self.chat_model.generate_content(
                format_prompt,
                generation_config={
                    "temperature": 0,  # Deterministic output
                    "top_p": 0.95,
                    "top_k": 20,
                    "max_output_tokens": 2048,
                }
            )
            formatted = reformat_response.text
            print(f"  Formatted: {len(formatted)} chars")
            
            return formatted
            
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
                citation_parts.append(f"Paragraphs {', '.join(meta['paragraph_numbers'])}")
            
            citation = " | ".join(citation_parts) if citation_parts else "Unknown Source"
            
            # Limit text length for context window
            text = meta.get('full_text', 'No text available')
            if len(text) > 800:
                text = text[:800] + "..."
            
            formatted.append(f"""
[CHUNK {i}] {citation}
Year: {meta.get('year', 'N/A')} | Type: {meta.get('doc_type', 'Unknown')}
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
        if result['filters']['risk_category']:
            print(f"Risk Category: {result['filters']['risk_category']}")
        if result['filters']['year_filter']:
            print(f"Year Filter: >= {result['filters']['year_filter']}")
        print(f"Total Results: {result['num_results']}")
        
        print(f"\n{'─'*80}")
        print(f"TOP 5 MATCHES:")
        print(f"{'─'*80}")
        
        for i, chunk in enumerate(result['top_chunks'][:5], 1):
            meta = chunk['metadata']
            print(f"\n{i}. {meta.get('regulation_name', 'Unknown')}")
            print(f"   Article: {meta.get('article_number', 'N/A')} | Year: {meta.get('year', 'N/A')}")
            print(f"   Score: {chunk['score']:.3f}")
            print(f"   Text: {meta.get('full_text', '')[:150]}...")
        
        if result['llm_analysis']:
            print(f"\n{'='*80}")
            print(f"LLM ANALYSIS")
            print(f"{'='*80}")
            print(result['llm_analysis'])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Query EU legislation using RAG system'
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
        help='GCP region'
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
        default=DEPLOYED_INDEX_ID,
        help='Deployed index ID'
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
        choices=list(EULegislationRAG.RISK_CATEGORIES.keys()),
        help='Filter by risk category'
    )
    parser.add_argument(
        '--year-filter',
        type=int,
        help='Minimum year filter (e.g., 2016)'
    )
    parser.add_argument(
        '--top-k',
        type=int,
        default=50,
        help='Number of results to retrieve'
    )
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Skip LLM analysis'
    )
    parser.add_argument(
        '--include-same-regulation',
        action='store_true',
        help='Include contradictions/overlaps within the same regulation (default: only cross-regulation)'
    )
    parser.add_argument(
        '--no-query-expansion',
        action='store_true',
        help='Disable query expansion (faster but lower recall)'
    )
    parser.add_argument(
        '--metadata-file',
        type=str,
        default='metadata_store_production.pkl',
        help='Path to metadata pickle file (default: metadata_store_production.pkl)'
    )
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = EULegislationRAG(
        project_id=args.project_id,
        location=args.location,
        index_endpoint_name=args.index_endpoint,
        deployed_index_id=args.deployed_index_id,
        metadata_file=args.metadata_file
    )
    
    # Execute query
    result = rag.query(
        user_query=args.query,
        risk_category=args.risk_category,
        year_filter=args.year_filter,
        top_k=args.top_k,
        analyze_with_llm=not args.no_llm,
        focus_cross_regulation=not args.include_same_regulation,
        use_query_expansion=not args.no_query_expansion
    )
    
    # Print results
    rag.print_results(result)


if __name__ == "__main__":
    main()
