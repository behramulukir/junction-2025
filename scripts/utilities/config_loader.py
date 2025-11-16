#!/usr/bin/env python3
"""
Centralized configuration loader for all scripts
Loads config.yaml and provides easy access to settings
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager with environment support."""
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "production"):
        """Initialize configuration.
        
        Args:
            config_path: Path to config.yaml (auto-detected if None)
            environment: Environment name (development/staging/production)
        """
        self.environment = environment
        
        # Auto-detect config path if not provided
        if config_path is None:
            # Try repo root first
            repo_root = Path(__file__).parent.parent.parent
            config_path = repo_root / "config.yaml"
            
            if not config_path.exists():
                # Try current directory
                config_path = Path("config.yaml")
        
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Load config
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Apply environment overrides
        self._apply_environment_overrides()
        
        print(f"✅ Loaded configuration (environment: {environment})")
    
    def _apply_environment_overrides(self):
        """Apply environment-specific overrides."""
        if 'environments' not in self._config:
            return
        
        env_config = self._config['environments'].get(self.environment, {})
        if not env_config:
            return
        
        # Deep merge environment config
        self._deep_merge(self._config, env_config)
    
    def _deep_merge(self, base: Dict, override: Dict):
        """Deep merge override dict into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path.
        
        Args:
            path: Dot-separated path (e.g., 'gcp.project_id')
            default: Default value if path not found
            
        Returns:
            Configuration value
            
        Example:
            config.get('gcp.project_id')
            config.get('vector_search.index.algorithm')
        """
        parts = path.split('.')
        value = self._config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section.
        
        Args:
            section: Section name (e.g., 'gcp', 'vector_search')
            
        Returns:
            Section dictionary
        """
        return self._config.get(section, {})
    
    # Convenience properties for common configs
    @property
    def project_id(self) -> str:
        """GCP project ID."""
        return self.get('gcp.project_id')
    
    @property
    def location(self) -> str:
        """GCP location/region."""
        return self.get('gcp.location', 'europe-west1')
    
    @property
    def bucket_name(self) -> str:
        """GCS bucket name."""
        return self.get('gcp.bucket_name')
    
    @property
    def embedding_model(self) -> str:
        """Embedding model name."""
        return self.get('vector_search.embeddings.model', 'text-multilingual-embedding-002')
    
    @property
    def llm_model(self) -> str:
        """LLM model name."""
        return self.get('rag.llm.model', 'gemini-2.5-pro')
    
    @property
    def metadata_source(self) -> str:
        """Primary metadata source."""
        return self.get('rag.metadata.source', 'metadata_store_production.pkl')
    
    @property
    def metadata_fallbacks(self) -> list:
        """Metadata fallback sources."""
        return self.get('rag.metadata.fallback_sources', [])
    
    def get_index_config(self) -> Dict[str, Any]:
        """Get complete index configuration for building."""
        return {
            'project_id': self.project_id,
            'location': self.location,
            'bucket_name': self.bucket_name,
            'embeddings_prefix': self.get('vector_search.embeddings.gcs_prefix'),
            'display_name': self.get('vector_search.index.display_name'),
            'algorithm': self.get('vector_search.index.algorithm'),
            'dimensions': self.get('vector_search.index.dimensions'),
            'distance_measure': self.get('vector_search.index.distance_measure'),
            'shard_size': self.get('vector_search.index.shard_size'),
            'approximate_neighbors_count': self.get('vector_search.index.approximate_neighbors_count'),
            'leaf_node_embedding_count': self.get('vector_search.index.leaf_node_embedding_count'),
            'leaf_nodes_to_search_percent': self.get('vector_search.index.leaf_nodes_to_search_percent'),
        }
    
    def get_endpoint_config(self) -> Dict[str, Any]:
        """Get complete endpoint configuration for deployment."""
        return {
            'project_id': self.project_id,
            'location': self.location,
            'display_name': self.get('vector_search.endpoint.display_name'),
            'public_endpoint_enabled': self.get('vector_search.endpoint.public_endpoint_enabled'),
            'machine_type': self.get('vector_search.endpoint.machine_type'),
            'min_replicas': self.get('vector_search.endpoint.min_replicas'),
            'max_replicas': self.get('vector_search.endpoint.max_replicas'),
            'enable_access_logging': self.get('vector_search.endpoint.enable_access_logging'),
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get complete RAG configuration."""
        return {
            'project_id': self.project_id,
            'location': 'us-central1',  # Gemini is only in us-central1
            'embedding_model': self.embedding_model,
            'llm_model': self.llm_model,
            'metadata_source': self.metadata_source,
            'metadata_fallbacks': self.metadata_fallbacks,
            'search': self.get_section('rag')['search'],
            'llm': self.get_section('rag')['llm'],
            'risk_categories': self.get_section('rag')['risk_categories'],
        }


# Global config instance
_global_config: Optional[Config] = None


def get_config(environment: Optional[str] = None, force_reload: bool = False) -> Config:
    """Get or create global config instance.
    
    Args:
        environment: Environment name (auto-detected from ENV var if None)
        force_reload: Force reload configuration
        
    Returns:
        Config instance
    """
    global _global_config
    
    if force_reload or _global_config is None:
        # Auto-detect environment from env var
        if environment is None:
            environment = os.environ.get('APP_ENV', 'production')
        
        _global_config = Config(environment=environment)
    
    return _global_config


def load_config(config_path: Optional[str] = None, 
                environment: Optional[str] = None) -> Config:
    """Load configuration (convenience function).
    
    Args:
        config_path: Path to config.yaml
        environment: Environment name
        
    Returns:
        Config instance
    """
    if environment is None:
        environment = os.environ.get('APP_ENV', 'production')
    
    return Config(config_path=config_path, environment=environment)


if __name__ == "__main__":
    # Test configuration loader
    import sys
    import json
    
    env = sys.argv[1] if len(sys.argv) > 1 else "production"
    
    print(f"\n{'='*80}")
    print(f"Testing Configuration Loader (environment: {env})")
    print(f"{'='*80}\n")
    
    config = load_config(environment=env)
    
    print("GCP Configuration:")
    print(f"  Project ID: {config.project_id}")
    print(f"  Location: {config.location}")
    print(f"  Bucket: {config.bucket_name}")
    
    print("\nVector Search Configuration:")
    index_config = config.get_index_config()
    print(f"  Index: {index_config['display_name']}")
    print(f"  Algorithm: {index_config['algorithm']}")
    print(f"  Dimensions: {index_config['dimensions']}")
    
    print("\nEndpoint Configuration:")
    endpoint_config = config.get_endpoint_config()
    print(f"  Endpoint: {endpoint_config['display_name']}")
    print(f"  Machine Type: {endpoint_config['machine_type']}")
    print(f"  Replicas: {endpoint_config['min_replicas']}-{endpoint_config['max_replicas']}")
    
    print("\nRAG Configuration:")
    rag_config = config.get_rag_config()
    print(f"  Embedding Model: {rag_config['embedding_model']}")
    print(f"  LLM Model: {rag_config['llm_model']}")
    print(f"  Metadata Source: {rag_config['metadata_source']}")
    print(f"  Risk Categories: {len(rag_config['risk_categories'])} defined")
    
    print("\n✅ Configuration test complete!")
