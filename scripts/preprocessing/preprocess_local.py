#!/usr/bin/env python3
"""
EU Legislation Document Preprocessing Pipeline (Local + gsutil)

This script:
1. Scans the workspace for EU legislation JSON files
2. Filters out non-content files (*.doc.json, *.toc.fmx.json)
3. Chunks documents by semantic boundaries (Articles, Recitals)
4. Extracts metadata (regulation names, article numbers, citations)
5. Saves processed chunks locally as JSONL files
6. Uses gsutil CLI to upload to Google Cloud Storage

Usage:
    python preprocess_local.py --config config.yaml
    
    # Then upload with:
    gsutil -m cp -r processed_chunks/ gs://your-bucket-name/
"""

import json
import re
import os
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import yaml
import tiktoken
from tqdm import tqdm


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""
    document_id: str  # UUID from directory or composite ID
    filename: str  # Original filename
    regulation_name: str  # Extracted regulation name
    year: Optional[int]  # Extracted year
    doc_type: str  # e.g., "Commission Implementing Regulation"
    chunk_id: int  # Sequential chunk number within document
    chunk_type: str  # "article", "recital", "section", "chapter", "annex", "mixed"
    article_number: Optional[str]  # e.g., "5" or "1 §"
    paragraph_numbers: List[str]  # e.g., ["(5)", "(6)"] or ["Chapter 1", "Section 1"]
    full_text: str  # The actual chunk text
    paragraph_indices: List[Tuple[int, int]]  # Start/end char positions of each paragraph in full_text
    char_start: int  # Character offset in original document
    char_end: int  # Character offset end
    token_count: int  # Approximate token count
    regulation_refs: List[str]  # Referenced regulations (e.g., ["EC No 1334/2003"])
    language: str  # Language code: 'en', 'fi', 'multi'
    source_type: str  # 'eu_legislation', 'national_law', 'international_standard'


@dataclass
class DocumentInfo:
    """Information about a source document."""
    document_id: str
    filename: str
    file_path: str
    paragraphs: List[str]
    full_text: str
    source_type: str  # 'eu_legislation', 'national_law', 'international_standard'
    language: str  # Detected language: 'en', 'fi', 'multi'


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
            
            # Determine source type and generate appropriate document ID
            parts = file_path.parts
            source_type, document_id = self._extract_source_info(file_path, parts)
            
            full_text = "\n".join(paragraphs)
            
            # Detect language
            language = self._detect_language(full_text[:1000])
            
            return DocumentInfo(
                document_id=document_id,
                filename=file_path.name,
                file_path=str(file_path),
                paragraphs=paragraphs,
                full_text=full_text,
                source_type=source_type,
                language=language
            )
        
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _extract_source_info(self, file_path: Path, parts: tuple) -> Tuple[str, str]:
        """Extract source type and generate document ID based on file structure."""
        import hashlib
        
        # Check for EU legislation structure: .../output/{UUID}/fmx4/{filename}.json
        if 'output' in parts:
            uuid_idx = parts.index('output') + 1
            if uuid_idx < len(parts):
                document_id = parts[uuid_idx]
                return 'eu_legislation', document_id
        
        # Check for national laws: .../other_national_laws/{filename}.di.json
        if 'other_national_laws' in parts:
            # Generate composite UUID from filename
            filename_base = file_path.stem.replace('.di', '')  # Remove .di from stem
            composite_id = f"nat-law-{filename_base}"
            return 'national_law', composite_id
        
        # Check for international standards: .../other_regulation_standards/{category}/{filename}.di.json
        if 'other_regulation_standards' in parts:
            std_idx = parts.index('other_regulation_standards') + 1
            category = parts[std_idx] if std_idx < len(parts) else 'unknown'
            filename_base = file_path.stem.replace('.di', '')
            composite_id = f"std-{category.lower()}-{filename_base}"
            return 'international_standard', composite_id
        
        # Fallback: generate hash-based ID
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:16]
        return 'unknown', f"doc-{file_hash}"
    
    def _detect_language(self, text_sample: str) -> str:
        """Detect document language based on content indicators."""
        # Finnish language indicators
        finnish_indicators = ['§', 'luku', 'Laki', 'laki', 'momentti', 'pykälä', 
                             'säädös', 'asetus', 'Asetus', 'ministeriö']
        finnish_count = sum(1 for indicator in finnish_indicators if indicator in text_sample)
        
        # English indicators
        english_indicators = ['Article', 'Regulation', 'Directive', 'shall', 'pursuant',
                             'Commission', 'Council', 'Parliament']
        english_count = sum(1 for indicator in english_indicators if indicator in text_sample)
        
        # Determine language
        if finnish_count > 3:
            if english_count > 2:
                return 'multi'  # Mixed language document
            return 'fi'
        elif english_count > 0:
            return 'en'
        
        return 'en'  # Default to English


# ============================================================================
# Metadata Extractor
# ============================================================================

class MetadataExtractor:
    """Extracts regulation names, years, document types, and references."""
    
    # EU Legislation patterns
    REGULATION_PATTERN = re.compile(
        r'(Commission|Council|European Parliament|Directive|Regulation|Decision|Corrigendum to)\s+'
        r'(?:Implementing|Delegated|Amending)?\s*'
        r'(Regulation|Directive|Decision)\s+'
        r'\((EU|EC|EEC)\)\s+'
        r'(?:No\s+)?'
        r'(\d{4}/\d+|\d+/\d{4})',
        re.IGNORECASE
    )
    
    # Finnish/National Law patterns
    FINNISH_ACT_PATTERN = re.compile(
        r'(Laki|Act|laki)\s+(?:on\s+)?([^(\n]+?)\s*\((\d{1,4}/\d{4})',
        re.IGNORECASE
    )
    
    # International Standards patterns (Basel, IFRS, etc.)
    STANDARD_PATTERN = re.compile(
        r'(Basel|IFRS|MiFID|MiFIR|CRD|CRR|BRRD|EBA|SFDR)\s*(Framework|Standard|Directive|Regulation)?\s*([IVX]+)?',
        re.IGNORECASE
    )
    
    # CELEX number pattern for EU documents
    CELEX_PATTERN = re.compile(
        r'CELEX[_:]?(\d{5}[A-Z]\d{4})',
        re.IGNORECASE
    )
    
    YEAR_PATTERN = re.compile(r'\b(19\d{2}|20\d{2})\b')
    
    # Enhanced document type pattern (multilingual)
    DOC_TYPE_PATTERN = re.compile(
        r'^(?:(Commission|Council|European Parliament|Ministry)\s+)?'
        r'(?:(Implementing|Delegated|Amending)\s+)?'
        r'(Regulation|Directive|Decision|Corrigendum|Act|Laki|Framework|Standard)',
        re.IGNORECASE
    )
    
    # Enhanced reference pattern
    REF_PATTERN = re.compile(
        r'\((EU|EC|EEC)\)\s+(?:No\s+)?(\d{4}/\d+|\d+/\d{4})',
        re.IGNORECASE
    )
    
    @staticmethod
    def extract_regulation_name(first_paragraph: str, source_type: str = 'eu_legislation') -> str:
        """Extract the main regulation name from first paragraph."""
        try:
            # Limit search to first 800 chars to prevent regex issues
            search_text = first_paragraph[:800]
            lines = search_text.split('\n')
            
            # For national laws, skip page numbers and translation notes
            if source_type == 'national_law':
                for i, line in enumerate(lines[:15]):  # Check first 15 lines
                    line = line.strip()
                    
                    # Skip page numbers like "1(77)", "2(77)"
                    if len(line) < 10 and '(' in line and line[0].isdigit():
                        continue
                    
                    # Skip translation notes
                    if 'translation from' in line.lower() or 'legally binding' in line.lower():
                        continue
                    
                    # Skip ministry attribution
                    if 'ministry of' in line.lower():
                        continue
                    
                    # Look for "Act on..." or "Laki..." - the actual title
                    if ('Act on' in line or 'Laki' in line) and len(line) > 20:
                        # Clean up - remove extra info after parentheses
                        if '(' in line and line.count('(') > 1:
                            # Keep everything up to and including the first closing paren
                            match = re.search(r'^(.+?\)\s*(?:\(.+?\))?)', line)
                            if match:
                                return match.group(1).strip()
                        return line
            
            # Try EU regulation pattern first
            match = MetadataExtractor.REGULATION_PATTERN.search(search_text)
            if match:
                return match.group(0)
            
            # Try Finnish Act pattern
            match = MetadataExtractor.FINNISH_ACT_PATTERN.search(search_text)
            if match:
                # Return full act name with number
                return match.group(0)
            
            # Try international standard pattern
            match = MetadataExtractor.STANDARD_PATTERN.search(search_text)
            if match:
                return match.group(0)
            
            # Try CELEX pattern
            match = MetadataExtractor.CELEX_PATTERN.search(search_text)
            if match:
                return f"CELEX {match.group(1)}"
            
        except Exception:
            pass
        
        # Fallback: use first substantial line (skip page numbers, etc.)
        lines = first_paragraph.split('\n')
        for line in lines[:5]:
            cleaned = line.strip()
            if len(cleaned) > 20 and not cleaned.isdigit():
                return cleaned[:150]
        
        return first_paragraph[:100].strip()
    
    @staticmethod
    def extract_year(text: str, filename: str = '') -> Optional[int]:
        """Extract year from text with filename fallback."""
        matches = MetadataExtractor.YEAR_PATTERN.findall(text)
        if matches:
            # Return the most recent year found (already full 4-digit years)
            years = [int(year) for year in matches]
            return max(years)
        
        # Fallback: extract from filename (e.g., "444_2017.di.json" -> 2017)
        if filename:
            filename_matches = re.findall(r'\b(19|20)\d{2}\b', filename)
            if filename_matches:
                return int(filename_matches[-1])  # Use last year in filename
        
        return None
    
    @staticmethod
    def extract_doc_type(first_paragraph: str, source_type: str = 'eu_legislation') -> str:
        """Extract document type."""
        # Try standard pattern
        match = MetadataExtractor.DOC_TYPE_PATTERN.search(first_paragraph)
        if match:
            parts = [p for p in match.groups() if p]
            doc_type = " ".join(parts)
            # Normalize Finnish to English
            if 'Laki' in doc_type and 'Act' not in doc_type:
                doc_type = doc_type.replace('Laki', 'Act')
            return doc_type
        
        # Check for international standards
        if source_type == 'international_standard':
            for keyword in ['Framework', 'Standard', 'Guideline', 'Directive', 'Regulation']:
                if keyword.lower() in first_paragraph[:500].lower():
                    return keyword
        
        # Check for Finnish specific document types
        if source_type == 'national_law':
            search_lower = first_paragraph[:500].lower()
            if 'laki' in search_lower or 'act' in search_lower:
                return 'Act'
            if 'asetus' in search_lower:
                return 'Decree'
        
        return "Unknown"
    
    @staticmethod
    def extract_regulation_refs(text: str) -> List[str]:
        """Extract all regulation references from text."""
        try:
            # Search full text for better reference extraction
            matches = MetadataExtractor.REF_PATTERN.findall(text)
            refs = set()
            for match in matches:
                refs.add(f"{match[0]} No {match[1]}")
            return sorted(list(refs))
        except Exception:
            return []


# ============================================================================
# Document Chunker
# ============================================================================

class DocumentChunker:
    """Chunks documents by semantic boundaries."""
    
    def __init__(self, config: Config):
        self.config = config  # Store config for later use
        self.article_pattern = re.compile(config.get('chunking', 'article_pattern'))
        self.recital_pattern = re.compile(config.get('chunking', 'recital_pattern'))
        self.section_pattern = re.compile(config.get('chunking', 'section_pattern'))
        
        # Finnish patterns
        self.finnish_section_pattern = re.compile(r'^(Section\s+\d+|^\d+\s*§)')  # "Section 1" or "1 §"
        self.finnish_chapter_pattern = re.compile(r'^(Chapter|Luku)\s+\d+', re.IGNORECASE)  # "Chapter 1" or "Luku 1"
        self.finnish_subsection_pattern = re.compile(r'^\(\d+\)')  # Finnish subsections like "(1)"
        
        # International standard patterns
        self.framework_section_pattern = re.compile(r'^(Part|Section|Chapter|Annex)\s+[IVX\d]+', re.IGNORECASE)
        
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
        try:
            # Limit very long texts to prevent encoding issues
            if len(text) > 50000:
                # Estimate: ~4 chars per token
                return len(text) // 4
            return len(self.encoder.encode(text))
        except Exception as e:
            self.logger.warning(f"Token counting failed, estimating: {e}")
            return len(text) // 4  # Rough estimate: 4 chars per token
    
    def split_at_sentences(self, text: str, max_tokens: int) -> List[str]:
        """Split text at sentence boundaries to avoid mid-sentence breaks.
        
        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks split at sentence boundaries
        """
        # Sentence boundary regex - handles common patterns
        sentence_pattern = re.compile(
            r'(?<=[.!?])\s+(?=[A-Z])|'  # Period/!/?  followed by space and capital
            r'(?<=[.!?])[\n]+|'  # Period/!/? followed by newline(s)
            r'(?<=\d\))\s+(?=[A-Z])|'  # Numbered list item
            r';\s+(?=[A-Z])'  # Semicolon followed by capital (legal text)
        )
        
        sentences = sentence_pattern.split(text)
        if not sentences or len(sentences) == 1:
            # No clear sentence boundaries or single sentence
            return [text]
        
        chunks = []
        current = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sent_tokens = self.count_tokens(sentence)
            
            # If single sentence exceeds max, keep it as-is
            if sent_tokens > max_tokens:
                if current:
                    chunks.append(' '.join(current))
                    current = []
                    current_tokens = 0
                chunks.append(sentence)
                continue
            
            # If adding this sentence would exceed max, start new chunk
            if current and current_tokens + sent_tokens > max_tokens:
                chunks.append(' '.join(current))
                current = [sentence]
                current_tokens = sent_tokens
            else:
                current.append(sentence)
                current_tokens += sent_tokens
        
        if current:
            chunks.append(' '.join(current))
        
        return chunks
    
    def ends_at_sentence_boundary(self, text: str) -> bool:
        """Check if text ends at a natural sentence boundary.
        
        Returns:
            True if text ends at sentence boundary, False otherwise
        """
        if not text:
            return False
        
        text = text.rstrip()
        
        # Good endings: period, exclamation, question mark, semicolon
        if text[-1] in '.!?;':
            return True
        
        # Colon is good if followed by newline (end of heading/title)
        if text[-1] == ':':
            return True
        
        # Check for numbered/lettered list items: "(5)", "(a)", "5.", "a)"
        if re.search(r'[\(\[]?[a-z0-9]+[\)\]]?\.?$', text, re.IGNORECASE):
            return True
        
        # Check for legal citations ending properly
        if re.search(r'\d{4}/\d+[A-Z]*$', text):  # e.g., "2016/869"
            return True
        
        # Check for article/paragraph references
        if re.search(r'(Article|paragraph|point)\s+\d+[a-z]?$', text, re.IGNORECASE):
            return True
        
        return False
    
    def should_keep_together(self, current_paras: List[str], next_para: str, current_article: Optional[str]) -> bool:
        """Determine if next paragraph should stay with current chunk for semantic coherence.
        
        Args:
            current_paras: Current chunk paragraphs
            next_para: Next paragraph to consider
            current_article: Current article number if any
            
        Returns:
            True if should keep together, False if should split
        """
        if not current_paras:
            return False
        
        # Check if current chunk ends mid-sentence
        last_para = current_paras[-1]
        if not self.ends_at_sentence_boundary(last_para):
            # Complete the sentence/thought
            return True
        
        # Check if next paragraph references current article
        if current_article:
            if re.search(rf'\barticle\s+{current_article}\b', next_para, re.IGNORECASE):
                return True
            # Check for "paragraph X" references (referencing current context)
            if re.search(r'\b(paragraph|subparagraph|point)\s+\d+\b', next_para, re.IGNORECASE):
                return True
        
        # Check if next para starts with continuation words
        continuation_patterns = [
            r'^(however|moreover|furthermore|in addition|additionally|therefore|thus)',
            r'^(where|when|if|unless|provided that)',
            r'^(such|those|these|that|which)',
        ]
        
        next_para_lower = next_para.lower().strip()
        for pattern in continuation_patterns:
            if re.match(pattern, next_para_lower):
                return True
        
        return False
    
    def calculate_overlap(self, paragraphs: List[str], target_tokens: int) -> List[str]:
        """Calculate overlap paragraphs ensuring complete sentences.
        
        Args:
            paragraphs: Paragraphs from previous chunk
            target_tokens: Target token count for overlap
            
        Returns:
            List of paragraphs to use as overlap (from end of chunk)
        """
        if not paragraphs or target_tokens <= 0:
            return []
        
        overlap = []
        tokens = 0
        
        # Add complete paragraphs from end until we reach target
        for para in reversed(paragraphs):
            para_tokens = self.count_tokens(para)
            
            # Only add if it ends at sentence boundary
            if not self.ends_at_sentence_boundary(para):
                continue
            
            if tokens + para_tokens > target_tokens * 1.5 and overlap:  # Allow 50% overshoot
                break
            
            overlap.insert(0, para)
            tokens += para_tokens
            
            # Stop if we have good overlap
            if tokens >= target_tokens * 0.8:  # At least 80% of target
                break
        
        return overlap
    
    def detect_boundary(self, paragraph: str) -> Tuple[str, Optional[str], List[str]]:
        """
        Detect if paragraph is a structural boundary.
        
        Returns:
            (chunk_type, article_number, paragraph_numbers)
        """
        # Check for Finnish Chapter
        if self.finnish_chapter_pattern.match(paragraph):
            return ("chapter", None, [])
        
        # Check for Finnish Section (e.g., "Section 1" or "1 §")
        if self.finnish_section_pattern.match(paragraph):
            section_match = re.search(r'(?:Section\s+)?(\d+)\s*§?', paragraph)
            section_num = f"{section_match.group(1)} §" if section_match else None
            return ("section", section_num, [])
        
        # Check for Article (EU legislation)
        if self.article_pattern.match(paragraph):
            article_match = re.search(r'Article\s+(\d+)', paragraph)
            article_num = article_match.group(1) if article_match else None
            return ("article", article_num, [])
        
        # Check for Recital
        if self.recital_pattern.match(paragraph):
            recital_match = re.search(r'\((\d+)\)', paragraph)
            recital_num = f"({recital_match.group(1)})" if recital_match else None
            return ("recital", None, [recital_num] if recital_num else [])
        
        # Check for Framework sections (Basel, IFRS, etc.)
        if self.framework_section_pattern.match(paragraph):
            return ("section", None, [])
        
        # Check for generic Section
        if self.section_pattern.match(paragraph):
            return ("section", None, [])
        
        return ("paragraph", None, [])
    
    def chunk_document(self, doc: DocumentInfo) -> List[ChunkMetadata]:
        """Chunk document into semantic chunks with smart boundary detection."""
        chunks = []
        current_chunk_paras = []
        current_chunk_type = "mixed"
        current_article = None
        current_paragraph_nums = []
        char_offset = 0
        
        # Get chunking config
        enable_overlap = self.config.get('chunking', 'enable_overlap', default=False)
        overlap_tokens = self.config.get('chunking', 'overlap_tokens', default=200)
        keep_related = self.config.get('chunking', 'keep_related_articles', default=True)
        max_para_tokens = self.config.get('chunking', 'max_paragraph_tokens', default=1800)
        
        # Extract metadata from first few paragraphs with source type awareness
        # For national laws, we need to look at multiple paragraphs to skip page numbers
        first_text = '\n'.join(doc.paragraphs[:20]) if doc.source_type == 'national_law' else doc.paragraphs[0]
        regulation_name = MetadataExtractor.extract_regulation_name(first_text, doc.source_type)
        year = MetadataExtractor.extract_year(first_text, doc.filename)
        doc_type = MetadataExtractor.extract_doc_type(first_text, doc.source_type)
        regulation_refs = MetadataExtractor.extract_regulation_refs(doc.full_text)
        
        # Create document header for first chunk context
        doc_header = self._create_document_header(doc, regulation_name, year, doc_type)
        
        for para_idx, para in enumerate(doc.paragraphs):
            para_type, article_num, para_nums = self.detect_boundary(para)
            para_tokens = self.count_tokens(para)
            
            # Handle oversized paragraphs by splitting at sentence boundaries
            if para_tokens > max_para_tokens:
                sub_paras = self.split_at_sentences(para, max_para_tokens)
                self.logger.debug(f"Split oversized paragraph ({para_tokens} tokens) into {len(sub_paras)} parts")
            else:
                sub_paras = [para]
            
            for sub_para in sub_paras:
                sub_para_tokens = self.count_tokens(sub_para)
                
                # Check if we should start a new chunk
                should_split = False
                
                if current_chunk_paras:
                    current_tokens = self.count_tokens("\n".join(current_chunk_paras))
                    
                    # SMART SPLITTING LOGIC
                    
                    # 1. Never split if it would create mid-sentence break (unless exceeding hard limit)
                    if keep_related and self.should_keep_together(current_chunk_paras, sub_para, current_article):
                        if current_tokens + sub_para_tokens <= self.max_chunk_tokens * 1.2:  # Allow 20% overshoot
                            should_split = False
                        else:
                            # Must split due to size, but log it
                            self.logger.debug(f"Forced split despite semantic connection (tokens: {current_tokens + sub_para_tokens})")
                            should_split = True
                    
                    # 2. Split at major boundaries if chunk is already large enough
                    elif para_type in ["article", "section"] and current_tokens >= self.min_chunk_tokens:
                        # Only split if current chunk ends at good boundary
                        if self.ends_at_sentence_boundary(current_chunk_paras[-1]):
                            should_split = True
                    
                    # 3. Hard limit: must split if exceeding max tokens
                    elif current_tokens + sub_para_tokens > self.max_chunk_tokens:
                        should_split = True
                    
                    # 4. Soft split: reached target and at good boundary
                    elif current_tokens >= self.chunk_target_tokens and para_type in ["article", "recital", "section"]:
                        if self.ends_at_sentence_boundary(current_chunk_paras[-1]):
                            should_split = True
                
                if should_split:
                    # Save current chunk
                    chunk_text = "\n".join(current_chunk_paras)
                    
                    # Calculate paragraph indices BEFORE header injection
                    para_indices = []
                    pos = 0
                    
                    # If this is the first chunk and we're adding a header, offset all indices
                    if len(chunks) == 0 and doc_header:
                        header_offset = len(doc_header) + 2  # +2 for "\n\n"
                        chunk_text = doc_header + "\n\n" + chunk_text
                        pos = header_offset
                    
                    for p in current_chunk_paras:
                        start = pos
                        end = pos + len(p)
                        para_indices.append((start, end))
                        pos = end + 1  # +1 for newline
                    
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
                        regulation_refs=regulation_refs,
                        paragraph_indices=para_indices
                    ))
                    
                    char_offset += len(chunk_text) + 1  # +1 for newline
                    
                    # Calculate overlap if enabled
                    if enable_overlap:
                        overlap_paras = self.calculate_overlap(current_chunk_paras, overlap_tokens)
                        current_chunk_paras = overlap_paras
                        # Don't reset paragraph_nums if we have overlap
                        if not overlap_paras:
                            current_paragraph_nums = []
                    else:
                        # Reset without overlap
                        current_chunk_paras = []
                        current_paragraph_nums = []
                
                # Add paragraph to current chunk
                current_chunk_paras.append(sub_para)
                
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
            
            # Calculate paragraph indices BEFORE header injection
            para_indices = []
            pos = 0
            
            # If this is the first chunk and we're adding a header, offset all indices
            if len(chunks) == 0 and doc_header:
                header_offset = len(doc_header) + 2  # +2 for "\n\n"
                chunk_text = doc_header + "\n\n" + chunk_text
                pos = header_offset
            
            for p in current_chunk_paras:
                start = pos
                end = pos + len(p)
                para_indices.append((start, end))
                pos = end + 1  # +1 for newline
            
            chunk_tokens = self.count_tokens(chunk_text)
            
            # Handle orphans more intelligently
            if self.merge_orphans and chunks and chunk_tokens < self.orphan_threshold:
                # Check if merging would exceed max tokens
                prev_chunk = chunks[-1]
                merged_text = prev_chunk.full_text + "\n" + chunk_text
                merged_tokens = self.count_tokens(merged_text)
                
                if merged_tokens <= self.max_chunk_tokens * 1.2:  # Allow 20% overshoot for final merge
                    # Safe to merge - update paragraph indices
                    offset = len(prev_chunk.full_text) + 1  # +1 for newline
                    new_para_indices = []
                    pos = 0
                    for p in current_chunk_paras:
                        start = offset + pos
                        end = offset + pos + len(p)
                        new_para_indices.append((start, end))
                        pos += len(p) + 1
                    
                    prev_chunk.full_text = merged_text
                    prev_chunk.paragraph_indices.extend(new_para_indices)
                    prev_chunk.char_end = char_offset + len(chunk_text)
                    prev_chunk.token_count = merged_tokens
                    if current_paragraph_nums:
                        prev_chunk.paragraph_numbers.extend(current_paragraph_nums)
                    self.logger.debug(f"Merged orphan chunk ({chunk_tokens} tokens) with previous")
                else:
                    # Would be too large, keep as separate chunk
                    # Note: paragraph_indices already calculated correctly above for this chunk
                    pass
                    
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
                        regulation_refs=regulation_refs,
                        paragraph_indices=para_indices
                    ))
            else:
                # Use the para_indices calculated above (already accounts for header if needed)
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
                    regulation_refs=regulation_refs,
                    paragraph_indices=para_indices
                ))
        
        return chunks
    
    def _create_document_header(self,
                                doc: DocumentInfo,
                                regulation_name: str,
                                year: Optional[int],
                                doc_type: str) -> str:
        """Create a document header for chunk context.
        
        Args:
            doc: Document info
            regulation_name: Extracted regulation name
            year: Document year
            doc_type: Document type
            
        Returns:
            Formatted header string
        """
        parts = []
        
        # Add regulation name if meaningful (not just page numbers or "Unknown")
        if regulation_name and regulation_name not in ['Unknown', 'N/A'] and not regulation_name.startswith('1('):
            parts.append(regulation_name)
        
        # Add doc type if known
        if doc_type and doc_type != 'Unknown':
            if not parts:  # Only add if we don't have regulation name
                parts.append(doc_type)
            elif year:  # Add year in parentheses if we have both
                parts[0] = f"{parts[0]} ({year})"
                return parts[0]
        
        # Add year if available
        if year and not any(str(year) in p for p in parts):
            if parts:
                parts.append(f"({year})")
            else:
                parts.append(str(year))
        
        # Add source type for non-EU legislation
        if doc.source_type == 'national_law':
            parts.append("[National Law]")
        elif doc.source_type == 'international_standard':
            parts.append("[International Standard]")
        
        return " ".join(parts) if parts else ""
    
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
        regulation_refs: List[str],
        paragraph_indices: Optional[List[Tuple[int, int]]] = None
    ) -> ChunkMetadata:
        """Create chunk metadata object."""
        # Calculate paragraph indices if not provided
        if paragraph_indices is None:
            paragraph_indices = []
            char_pos = 0
            for para in chunk_text.split('\n'):
                start = char_pos
                end = char_pos + len(para)
                paragraph_indices.append((start, end))
                char_pos = end + 1  # +1 for newline
        
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
            paragraph_indices=paragraph_indices,
            char_start=char_start,
            char_end=char_start + len(chunk_text),
            token_count=self.count_tokens(chunk_text),
            regulation_refs=regulation_refs,
            language=doc.language,
            source_type=doc.source_type
        )


# ============================================================================
# Local File Writer
# ============================================================================

class LocalFileWriter:
    """Writes processed chunks to local filesystem as JSONL."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.file_counter = 0  # Track global file counter across multiple write calls
    
    def write_chunks(self, chunks: List[ChunkMetadata], batch_size: int = 1000) -> List[Path]:
        """Write chunks as JSONL files in batches."""
        if not chunks:
            return []
        
        self.logger.info(f"Writing {len(chunks)} chunks to {self.output_dir}...")
        
        written_files = []
        
        # Group into batches
        for batch_idx in range(0, len(chunks), batch_size):
            batch = chunks[batch_idx:batch_idx + batch_size]
            
            # Create JSONL content
            jsonl_lines = []
            for chunk in batch:
                jsonl_lines.append(json.dumps(asdict(chunk), ensure_ascii=False))
            
            jsonl_content = "\n".join(jsonl_lines)
            
            # Write to local file with global counter
            filename = f"chunks_batch_{self.file_counter:06d}.jsonl"
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(jsonl_content)
            
            written_files.append(file_path)
            self.logger.info(f"Written batch file {self.file_counter}: {filename} ({len(batch)} chunks)")
            self.file_counter += 1
        
        self.logger.info(f"Write complete: {len(chunks)} chunks in {len(written_files)} files")
        return written_files


# ============================================================================
# gsutil Uploader
# ============================================================================

class GsutilUploader:
    """Uploads files to GCS using gsutil CLI."""
    
    def __init__(self, bucket_name: str, output_prefix: str):
        self.bucket_name = bucket_name
        self.output_prefix = output_prefix
        self.logger = logging.getLogger(__name__)
    
    def check_gsutil(self) -> bool:
        """Check if gsutil is available."""
        try:
            result = subprocess.run(
                ['gsutil', 'version'],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"gsutil found: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("gsutil not found. Install with: https://cloud.google.com/storage/docs/gsutil_install")
            return False
    
    def upload_directory(self, local_dir: Path, use_parallel: bool = True) -> bool:
        """Upload entire directory to GCS using gsutil."""
        if not self.check_gsutil():
            return False
        
        gcs_path = f"gs://{self.bucket_name}/{self.output_prefix}/"
        
        self.logger.info(f"Uploading {local_dir} to {gcs_path}...")
        
        # Build gsutil command
        cmd = ['gsutil']
        
        # Use parallel composite uploads for faster transfer
        if use_parallel:
            cmd.append('-m')  # Multi-threaded/multi-processing
        
        cmd.extend(['cp', '-r', str(local_dir) + '/*', gcs_path])
        
        try:
            # Run gsutil command
            self.logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                check=True,
                text=True,
                capture_output=True
            )
            
            self.logger.info("Upload successful!")
            if result.stdout:
                self.logger.info(result.stdout)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Upload failed: {e}")
            if e.stderr:
                self.logger.error(e.stderr)
            return False
    
    def verify_upload(self) -> bool:
        """Verify files were uploaded successfully."""
        gcs_path = f"gs://{self.bucket_name}/{self.output_prefix}/"
        
        try:
            result = subprocess.run(
                ['gsutil', 'ls', gcs_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            file_count = len(result.stdout.strip().split('\n'))
            self.logger.info(f"Verification: Found {file_count} files in {gcs_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Verification failed: {e}")
            return False


# ============================================================================
# Main Pipeline
# ============================================================================

class PreprocessingPipeline:
    """Main preprocessing pipeline orchestrator."""
    
    def __init__(self, config_path: str):
        self.config = Config(config_path)
        self._setup_logging()
        
        # Support both single directory (legacy) and multiple directories
        input_dirs = self.config.get('processing', 'input_directories')
        if input_dirs is None:
            # Fallback to legacy single directory config
            input_dirs = [self.config.get('processing', 'input_directory', default='output')]
        
        # Create scanners for each input directory
        self.scanners = []
        for input_dir in input_dirs:
            self.scanners.append(DocumentScanner(
                base_path=input_dir,
                exclude_patterns=self.config.get('processing', 'exclude_patterns')
            ))
        
        self.chunker = DocumentChunker(self.config)
        
        # Local output directory
        self.local_output_dir = Path("processed_chunks")
        self.writer = LocalFileWriter(str(self.local_output_dir))
        
        # gsutil uploader
        self.uploader = GsutilUploader(
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
    
    def run(self, skip_upload: bool = False, use_batches: bool = True, batch_interval: int = 500):
        """Run the full preprocessing pipeline.
        
        Args:
            skip_upload: Skip gsutil upload step
            use_batches: Write chunks in batches during processing (recommended for large datasets)
            batch_interval: Number of documents to process before writing to disk (only if use_batches=True)
        """
        self.logger.info("=" * 80)
        self.logger.info("MULTILINGUAL LEGISLATION PREPROCESSING PIPELINE (Local + gsutil)")
        self.logger.info("=" * 80)
        
        # Step 1: Scan for files from all input directories
        self.logger.info("\n[STEP 1] Scanning for JSON files from multiple sources...")
        all_file_paths = []
        for scanner in self.scanners:
            file_paths = scanner.scan()
            all_file_paths.extend(file_paths)
            self.logger.info(f"  - {scanner.base_path}: {len(file_paths)} files")
        
        if not all_file_paths:
            self.logger.error("No files found to process!")
            return
        
        self.logger.info(f"Total files to process: {len(all_file_paths)}")
        
        # Step 2: Process documents with batch writing
        self.logger.info(f"\n[STEP 2] Processing {len(all_file_paths)} documents...")
        if use_batches:
            self.logger.info(f"  - Batch mode enabled: writing every {batch_interval} documents")
        else:
            self.logger.info(f"  - Batch mode disabled: writing all chunks at end")
        
        # Configuration for batch writing
        write_batch_size = batch_interval  # Write chunks every N documents to avoid memory buildup
        chunk_batch_size = self.config.get('output', 'batch_size', default=1000)
        
        all_chunks = []
        written_files = []
        errors = 0
        docs_processed = 0
        total_chunks_written = 0
        skipped_files = []  # Track skipped/failed files with reasons
        
        # Stats by source type
        source_stats = {'eu_legislation': 0, 'national_law': 0, 'international_standard': 0, 'unknown': 0}
        language_stats = {'en': 0, 'fi': 0, 'multi': 0}
        
        for idx, file_path in enumerate(tqdm(all_file_paths, desc="Processing documents")):
            try:
                # Periodic detailed logging to track progress
                if idx > 0 and idx % 100 == 0:
                    self.logger.debug(f"Processing file {idx}/{len(all_file_paths)}: {file_path.name}")
                
                # Load document (uses appropriate scanner based on file path)
                doc = None
                for scanner in self.scanners:
                    if file_path.is_relative_to(scanner.base_path):
                        doc = scanner.load_document(file_path)
                        break
                
                if not doc:
                    errors += 1
                    skipped_files.append(f"{file_path}\t[REASON: Failed to load or no paragraphs]")
                    continue
                
                # Track stats
                source_stats[doc.source_type] = source_stats.get(doc.source_type, 0) + 1
                language_stats[doc.language] = language_stats.get(doc.language, 0) + 1
                
                # Chunk document with timeout-like behavior
                try:
                    chunks = self.chunker.chunk_document(doc)
                    all_chunks.extend(chunks)
                    docs_processed += 1
                except Exception as chunk_error:
                    self.logger.error(f"Chunking failed for {file_path}: {chunk_error}")
                    errors += 1
                    skipped_files.append(f"{file_path}\t[REASON: Chunking error - {str(chunk_error)[:100]}]")
                    continue
                
                # Write to disk every write_batch_size documents to avoid memory buildup (if batch mode enabled)
                if use_batches and docs_processed % write_batch_size == 0:
                    self.logger.info(f"\n  → Flushing {len(all_chunks)} chunks to disk (processed {docs_processed}/{len(all_file_paths)} docs)...")
                    batch_files = self.writer.write_chunks(all_chunks, batch_size=chunk_batch_size)
                    written_files.extend(batch_files)
                    total_chunks_written += len(all_chunks)
                    all_chunks = []  # Clear memory
                
            except KeyboardInterrupt:
                self.logger.warning(f"\n\nInterrupted by user at document {docs_processed}")
                # Save what we have so far
                if all_chunks:
                    self.logger.info(f"Saving {len(all_chunks)} chunks before exit...")
                    batch_files = self.writer.write_chunks(all_chunks, batch_size=chunk_batch_size)
                    written_files.extend(batch_files)
                    total_chunks_written += len(all_chunks)
                raise
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                errors += 1
                skipped_files.append(f"{file_path}\t[REASON: Unexpected error - {str(e)[:100]}]")
        
        # Write any remaining chunks (or all chunks if batch mode disabled)
        if all_chunks:
            if use_batches:
                self.logger.info(f"\n  → Flushing final {len(all_chunks)} chunks to disk...")
            else:
                self.logger.info(f"\n  → Writing all {len(all_chunks)} chunks to disk...")
            batch_files = self.writer.write_chunks(all_chunks, batch_size=chunk_batch_size)
            written_files.extend(batch_files)
            total_chunks_written += len(all_chunks)
            all_chunks = []  # Clear memory
        
        self.logger.info(f"\nProcessing complete:")
        self.logger.info(f"  - Documents processed: {docs_processed}")
        self.logger.info(f"  - Errors: {errors}")
        self.logger.info(f"  - Total chunks created: {total_chunks_written}")
        
        # Display source type statistics
        self.logger.info(f"\nSource Type Statistics:")
        for source_type, count in source_stats.items():
            if count > 0:
                self.logger.info(f"  - {source_type}: {count} documents")
        
        # Display language statistics
        self.logger.info(f"\nLanguage Statistics:")
        for language, count in language_stats.items():
            if count > 0:
                lang_name = {'en': 'English', 'fi': 'Finnish', 'multi': 'Multilingual'}.get(language, language)
                self.logger.info(f"  - {lang_name}: {count} documents")
        
        # Save skipped files list
        if skipped_files:
            skipped_file_path = Path("skipped_files.txt")
            with open(skipped_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Skipped Files Report\n")
                f.write(f"# Total files scanned: {len(all_file_paths)}\n")
                f.write(f"# Successfully processed: {docs_processed}\n")
                f.write(f"# Skipped/Failed: {len(skipped_files)}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Format: <file_path>\\t[REASON: <reason>]\n\n")
                for entry in skipped_files:
                    f.write(f"{entry}\n")
            self.logger.info(f"  - Skipped files report saved to: {skipped_file_path.absolute()}")
        else:
            self.logger.info(f"  - No files were skipped!")
        
        # Step 3: Report written files
        self.logger.info(f"\n[STEP 3] Local files written:")
        self.logger.info(f"  - Location: {self.local_output_dir.absolute()}")
        self.logger.info(f"  - Files: {len(written_files)}")
        
        # Step 4: Upload to GCS with gsutil
        if not skip_upload:
            self.logger.info(f"\n[STEP 4] Uploading to Google Cloud Storage with gsutil...")
            
            success = self.uploader.upload_directory(self.local_output_dir, use_parallel=True)
            
            if success:
                self.logger.info("\n[STEP 5] Verifying upload...")
                self.uploader.verify_upload()
            else:
                self.logger.warning("\nUpload failed. You can manually upload with:")
                self.logger.warning(f"  gsutil -m cp -r {self.local_output_dir}/* gs://{self.config.get('gcp', 'bucket_name')}/{self.config.get('gcp', 'output_prefix')}/")
        else:
            self.logger.info(f"\n[STEP 4] Skipping upload (use --upload flag to enable)")
            self.logger.info(f"\nTo upload manually, run:")
            self.logger.info(f"  gsutil -m cp -r {self.local_output_dir}/* gs://{self.config.get('gcp', 'bucket_name')}/{self.config.get('gcp', 'output_prefix')}/")
        
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
        description='Preprocess EU legislation documents locally and upload with gsutil'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--skip-upload',
        action='store_true',
        help='Skip gsutil upload step (only process and save locally)'
    )
    parser.add_argument(
        '--no-batches',
        action='store_true',
        help='Disable batch writing (write all chunks at end). Not recommended for large datasets.'
    )
    parser.add_argument(
        '--batch-interval',
        type=int,
        default=500,
        help='Number of documents to process before writing to disk (default: 500)'
    )
    
    args = parser.parse_args()
    
    pipeline = PreprocessingPipeline(args.config)
    pipeline.run(
        skip_upload=args.skip_upload,
        use_batches=not args.no_batches,
        batch_interval=args.batch_interval
    )


if __name__ == '__main__':
    main()
