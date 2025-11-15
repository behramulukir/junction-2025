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
from metadata_store import init_metadata_store, get_metadata_store

# Configuration
PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "us-central1"
# Set these after running build_vector_index.py
INDEX_ENDPOINT_NAME = ""  # e.g., "projects/123/locations/us-central1/indexEndpoints/456"
DEPLOYED_INDEX_ID = "eu_legislation_deployed"


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
                 deployed_index_id: str):
        """Initialize the RAG system.
        
        Args:
            project_id: GCP project ID
            location: GCP region
            index_endpoint_name: Full resource name of the index endpoint
            deployed_index_id: ID of the deployed index
        """
        aiplatform.init(project=project_id, location=location)
        # Initialize vertexai with us-central1 for Gemini models
        vertexai.init(project=project_id, location="us-central1")
        
        self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")
        self.chat_model = GenerativeModel("gemini-2.5-pro")
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(index_endpoint_name)
        self.deployed_index_id = deployed_index_id
        
        # Initialize metadata store
        self.metadata_store = get_metadata_store()
        if len(self.metadata_store) == 0:
            print("  Loading metadata from processed chunks...")
            init_metadata_store("processed_chunks")
        
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
    
    def query(self, 
              user_query: str, 
              risk_category: Optional[str] = None,
              year_filter: Optional[int] = None,
              top_k: int = 50,
              analyze_with_llm: bool = True,
              focus_cross_regulation: bool = True) -> Dict:
        """Execute a search query and optionally analyze results with LLM.
        
        Args:
            user_query: Natural language query
            risk_category: Optional risk category filter
            year_filter: Optional minimum year filter (e.g., 2016)
            top_k: Number of similar chunks to retrieve
            analyze_with_llm: Whether to analyze results with Gemini
            focus_cross_regulation: If True, only report contradictions/overlaps between different regulations, not within same regulation
        
        Returns:
            Dict with search results and optional LLM analysis
        """
        print(f"\n{'='*80}")
        print(f"QUERY: {user_query}")
        print(f"{'='*80}")
        
        # Step 1: Vectorize query
        print("Generating query embedding...")
        query_embedding = self._get_embeddings_with_retry([user_query])[0].values
        
        # Step 2: Vector search
        print(f"Searching index (top {top_k})...")
        search_results = self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=top_k
        )
        
        # Extract neighbor IDs and fetch metadata from store
        neighbor_ids = [neighbor.id for neighbor in search_results[0]]
        metadata_map = self.metadata_store.get_batch(neighbor_ids)
        
        # Process results with metadata
        chunks = []
        for neighbor in search_results[0]:
            metadata = metadata_map.get(neighbor.id, {
                'id': neighbor.id,
                'full_text': 'Metadata not available'
            })
            
            # Apply filters
            if year_filter and metadata.get('year', 0) and metadata['year'] < year_filter:
                continue
            
            if risk_category and not self._matches_risk_category(metadata, risk_category):
                continue
            
            chunks.append({
                'score': float(neighbor.distance),
                'id': neighbor.id,
                'metadata': metadata
            })
        
        print(f"Found {len(chunks)} relevant chunks after filtering")
        
        # Step 3: LLM Analysis (optional)
        analysis = None
        if analyze_with_llm and chunks:
            print("Analyzing with Gemini LLM...")
            analysis = self._analyze_with_llm(user_query, chunks[:30], focus_cross_regulation)
        
        result = {
            'query': user_query,
            'filters': {
                'risk_category': risk_category,
                'year_filter': year_filter
            },
            'num_results': len(chunks),
            'top_chunks': chunks[:10],
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
        
        prompt = f"""You are a regulatory compliance analyst specializing in EU legislation analysis for financial institutions.

TASK: Analyze the following EU regulations for overlaps, contradictions, and relationships relevant to the query.

{analysis_scope}

USER QUERY: {query}

RELEVANT REGULATIONS:
{context}

ANALYSIS INSTRUCTIONS:
1. {contradiction_instruction}
2. {overlap_instruction}
3. Highlight ambiguous areas requiring legal interpretation
4. Note complementary relationships between regulations
5. Consider implications for financial institutions and banking sector

For each finding, provide:
- Regulation name + Article/Paragraph citation
- Exact relevant text (brief quote)
- Explanation of overlap/contradiction/relationship
- Severity: CRITICAL / HIGH / MEDIUM / LOW
- Practical impact for compliance

OUTPUT FORMAT: 
Use clear sections with headings:
- SUMMARY
- KEY FINDINGS (numbered list)
- CONTRADICTIONS (if any)
- OVERLAPS (if any)
- RECOMMENDATIONS

Be precise and cite specific articles. Focus on actionable insights.
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
    
    args = parser.parse_args()
    
    # Initialize RAG system
    rag = EULegislationRAG(
        project_id=args.project_id,
        location=args.location,
        index_endpoint_name=args.index_endpoint,
        deployed_index_id=args.deployed_index_id
    )
    
    # Execute query
    result = rag.query(
        user_query=args.query,
        risk_category=args.risk_category,
        year_filter=args.year_filter,
        top_k=args.top_k,
        analyze_with_llm=not args.no_llm,
        focus_cross_regulation=not args.include_same_regulation
    )
    
    # Print results
    rag.print_results(result)


if __name__ == "__main__":
    main()
