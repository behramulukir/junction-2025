#!/usr/bin/env python3
"""
Database caching layer for RAG responses
Stores generated content to avoid regenerating the same queries
"""

import sqlite3
import json
import hashlib
from typing import Optional, Dict, List
from datetime import datetime
import os


class ResponseCache:
    """SQLite-based cache for RAG responses."""
    
    def __init__(self, db_path: str = "rag_cache.db"):
        """Initialize cache database.
        
        Args:
            db_path: Path to SQLite database file (relative to backend directory)
        """
        # Ensure we use absolute path relative to this file's location
        if not os.path.isabs(db_path):
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(backend_dir, db_path)
        else:
            self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for regulation queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regulation_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                subcategory_id TEXT NOT NULL,
                subcategory_description TEXT NOT NULL,
                top_k INTEGER NOT NULL,
                regulations_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Table for analysis queries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE NOT NULL,
                subcategory_id TEXT NOT NULL,
                subcategory_description TEXT NOT NULL,
                top_k INTEGER NOT NULL,
                overlaps_json TEXT NOT NULL,
                contradictions_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """)
        
        # Create indexes for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_regulation_hash 
            ON regulation_cache(query_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_hash 
            ON analysis_cache(query_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_hash(self, subcategory_id: str, subcategory_description: str, top_k: int) -> str:
        """Generate unique hash for query parameters.
        
        Args:
            subcategory_id: Subcategory ID
            subcategory_description: Description text
            top_k: Number of results
            
        Returns:
            str: SHA256 hash
        """
        key = f"{subcategory_id}|{subcategory_description}|{top_k}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get_regulations(self, subcategory_id: str, subcategory_description: str, 
                       top_k: int) -> Optional[List[Dict]]:
        """Get cached regulations if available.
        
        Args:
            subcategory_id: Subcategory ID
            subcategory_description: Description text
            top_k: Number of results
            
        Returns:
            List of regulations or None if not cached
        """
        query_hash = self._generate_hash(subcategory_id, subcategory_description, top_k)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT regulations_json, access_count 
            FROM regulation_cache 
            WHERE query_hash = ?
        """, (query_hash,))
        
        result = cursor.fetchone()
        
        if result:
            # Update access stats
            cursor.execute("""
                UPDATE regulation_cache 
                SET last_accessed = CURRENT_TIMESTAMP,
                    access_count = ?
                WHERE query_hash = ?
            """, (result[1] + 1, query_hash))
            conn.commit()
            conn.close()
            
            return json.loads(result[0])
        
        conn.close()
        return None
    
    def cache_regulations(self, subcategory_id: str, subcategory_description: str,
                         top_k: int, regulations: List[Dict]):
        """Cache regulations response.
        
        Args:
            subcategory_id: Subcategory ID
            subcategory_description: Description text
            top_k: Number of results
            regulations: List of regulation dictionaries
        """
        query_hash = self._generate_hash(subcategory_id, subcategory_description, top_k)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO regulation_cache 
            (query_hash, subcategory_id, subcategory_description, top_k, regulations_json)
            VALUES (?, ?, ?, ?, ?)
        """, (query_hash, subcategory_id, subcategory_description, top_k, 
              json.dumps(regulations)))
        
        conn.commit()
        conn.close()
    
    def get_analysis(self, subcategory_id: str, subcategory_description: str,
                    top_k: int) -> Optional[Dict]:
        """Get cached analysis if available.
        
        Args:
            subcategory_id: Subcategory ID
            subcategory_description: Description text
            top_k: Number of results
            
        Returns:
            Dict with overlaps and contradictions or None if not cached
        """
        query_hash = self._generate_hash(subcategory_id, subcategory_description, top_k)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT overlaps_json, contradictions_json, access_count 
            FROM analysis_cache 
            WHERE query_hash = ?
        """, (query_hash,))
        
        result = cursor.fetchone()
        
        if result:
            # Update access stats
            cursor.execute("""
                UPDATE analysis_cache 
                SET last_accessed = CURRENT_TIMESTAMP,
                    access_count = ?
                WHERE query_hash = ?
            """, (result[2] + 1, query_hash))
            conn.commit()
            conn.close()
            
            return {
                'overlaps': json.loads(result[0]),
                'contradictions': json.loads(result[1])
            }
        
        conn.close()
        return None
    
    def cache_analysis(self, subcategory_id: str, subcategory_description: str,
                      top_k: int, overlaps: List[Dict], contradictions: List[Dict]):
        """Cache analysis response.
        
        Args:
            subcategory_id: Subcategory ID
            subcategory_description: Description text
            top_k: Number of results
            overlaps: List of overlap dictionaries
            contradictions: List of contradiction dictionaries
        """
        query_hash = self._generate_hash(subcategory_id, subcategory_description, top_k)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO analysis_cache 
            (query_hash, subcategory_id, subcategory_description, top_k, 
             overlaps_json, contradictions_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (query_hash, subcategory_id, subcategory_description, top_k,
              json.dumps(overlaps), json.dumps(contradictions)))
        
        conn.commit()
        conn.close()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), SUM(access_count) FROM regulation_cache")
        reg_stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*), SUM(access_count) FROM analysis_cache")
        analysis_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'regulations': {
                'cached_queries': reg_stats[0] or 0,
                'total_hits': reg_stats[1] or 0
            },
            'analysis': {
                'cached_queries': analysis_stats[0] or 0,
                'total_hits': analysis_stats[1] or 0
            }
        }
    
    def clear_cache(self):
        """Clear all cached data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM regulation_cache")
        cursor.execute("DELETE FROM analysis_cache")
        
        conn.commit()
        conn.close()
