#!/usr/bin/env python3
"""
Build Vertex AI Vector Search index from embeddings
"""

import sys
from pathlib import Path

# Add scripts/utilities to path for config_loader import
sys.path.insert(0, str(Path(__file__).parent.parent / "utilities"))

from google.cloud import aiplatform
import argparse
import time
from config_loader import get_config


def create_index(project_id: str, 
                 location: str, 
                 bucket_name: str,
                 embeddings_prefix: str,
                 display_name: str,
                 algorithm: str = "brute_force",
                 approximate_neighbors_count: int = 150):
    """Create vector search index with specified algorithm.
    
    Args:
        project_id: GCP project ID
        location: GCP region
        bucket_name: GCS bucket name
        embeddings_prefix: GCS prefix for embeddings
        display_name: Display name for the index
        algorithm: Algorithm to use - 'brute_force' or 'tree_ah'
        approximate_neighbors_count: Number of neighbors for tree_ah (ignored for brute_force)
        
    Returns:
        MatchingEngineIndex: Created index
    """
    aiplatform.init(project=project_id, location=location)
    
    print(f"Creating Vertex AI Vector Search index...")
    print(f"  Project: {project_id}")
    print(f"  Location: {location}")
    print(f"  Embeddings: gs://{bucket_name}/{embeddings_prefix}")
    print(f"  Algorithm: {algorithm.upper()}")
    
    if algorithm.lower() == "brute_force":
        # BRUTE_FORCE: Exact nearest neighbor search (100% recall)
        # Best for <500K vectors, faster build time
        print("Creating BRUTE_FORCE index (exact search, faster build)...")
        print("  Shard size: SHARD_SIZE_SMALL (for <500K vectors, allows e2-standard-4)")
        index = aiplatform.MatchingEngineIndex.create_brute_force_index(
            display_name=display_name,
            contents_delta_uri=f"gs://{bucket_name}/{embeddings_prefix}",
            dimensions=768,  # text-multilingual-embedding-002 dimensions
            distance_measure_type="DOT_PRODUCT_DISTANCE",  # For normalized embeddings
            shard_size="SHARD_SIZE_SMALL",  # Explicitly set for <500K vectors
            description=f"EU Legislation semantic search index (BRUTE_FORCE for exact search - 274K vectors)",
            labels={"env": "production", "dataset": "eu-legislation", "algorithm": "brute-force", "size": "274k"}
        )
    else:
        # TREE_AH: Approximate nearest neighbor search with ScaNN
        # Best for >500K vectors, lower latency, configurable recall
        print(f"Creating TREE_AH index (approximate search, {approximate_neighbors_count} neighbors)...")
        index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
            display_name=display_name,
            contents_delta_uri=f"gs://{bucket_name}/{embeddings_prefix}",
            dimensions=768,
            approximate_neighbors_count=approximate_neighbors_count,
            leaf_node_embedding_count=1000,  # Embeddings per leaf node
            leaf_nodes_to_search_percent=5.0,  # Search 5% of leaf nodes for balance
            distance_measure_type="DOT_PRODUCT_DISTANCE",
            shard_size="SHARD_SIZE_SMALL",  # For <500K vectors
            description=f"EU Legislation semantic search index (TREE_AH with {approximate_neighbors_count} neighbors)",
            labels={"env": "production", "dataset": "eu-legislation", "algorithm": "tree-ah"}
        )
    
    print(f"\n{'='*80}")
    print(f"INDEX READY!")
    print(f"{'='*80}")
    print(f"Resource name: {index.resource_name}")
    print(f"Index ID: {index.name}")
    print(f"\nSave this resource name for deployment!")
    
    return index


def deploy_index(project_id: str,
                 location: str,
                 index_name: str,
                 endpoint_display_name: str,
                 machine_type: str = "e2-standard-2",
                 min_replicas: int = 1,
                 max_replicas: int = 1):
    """Deploy index to an endpoint for serving.
    
    Args:
        project_id: GCP project ID
        location: GCP region
        index_name: Full resource name of the index
        endpoint_display_name: Display name for the endpoint
        machine_type: Machine type for serving
        min_replicas: Minimum number of replicas
        max_replicas: Maximum number of replicas
        
    Returns:
        MatchingEngineIndexEndpoint: Created endpoint
    """
    aiplatform.init(project=project_id, location=location)
    
    print(f"\nCreating index endpoint...")
    
    # Create endpoint
    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=endpoint_display_name,
        description="Endpoint for EU legislation semantic search",
        public_endpoint_enabled=True  # Set to False for VPC-only access
    )
    
    print(f"Endpoint created: {endpoint.resource_name}")
    print(f"\nDeploying index to endpoint (this takes ~30 minutes)...")
    
    # Get index object from resource name
    index = aiplatform.MatchingEngineIndex(index_name)
    
    # Deploy index to endpoint
    # Use unique deployed_index_id to avoid conflicts
    deployed_index_id = f"eu_legislation_prod_{index.name.split('/')[-1][-8:]}"
    print(f"  Machine type: {machine_type}")
    print(f"  Replicas: {min_replicas}-{max_replicas}")
    print(f"  Deployed index ID: {deployed_index_id}")
    
    endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        machine_type=machine_type,
        min_replica_count=min_replicas,
        max_replica_count=max_replicas,
        enable_access_logging=True,
    )
    
    print(f"\n{'='*80}")
    print(f"DEPLOYMENT COMPLETE!")
    print(f"{'='*80}")
    print(f"Endpoint: {endpoint.resource_name}")
    print(f"Deployed Index ID: eu_legislation_deployed")
    print(f"\nSave these for querying!")
    
    return endpoint


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build and deploy Vertex AI Vector Search index',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Support:
  Set APP_ENV environment variable to switch configurations:
    export APP_ENV=development   # Use dev config
    export APP_ENV=staging       # Use staging config  
    export APP_ENV=production    # Use production config (default)

Examples:
  # Create and deploy index with default config
  python build_vector_index.py
  
  # Deploy only mode with custom machine type
  python build_vector_index.py --deploy-only <index-resource-name> --machine-type e2-standard-8
  
  # Override config values
  python build_vector_index.py --project-id custom-project --algorithm tree_ah
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
        '--bucket-name',
        type=str,
        help='GCS bucket name (overrides config)'
    )
    parser.add_argument(
        '--embeddings-prefix',
        type=str,
        help='GCS prefix for embeddings (overrides config)'
    )
    parser.add_argument(
        '--index-display-name',
        type=str,
        help='Display name for the index (overrides config)'
    )
    parser.add_argument(
        '--endpoint-display-name',
        type=str,
        help='Display name for the endpoint (overrides config)'
    )
    parser.add_argument(
        '--algorithm',
        type=str,
        choices=['brute_force', 'tree_ah'],
        default='brute_force',
        help='Index algorithm: brute_force (exact, <500K vectors) or tree_ah (approximate, >500K vectors)'
    )
    parser.add_argument(
        '--approximate-neighbors-count',
        type=int,
        default=150,
        help='Number of neighbors for tree_ah algorithm (higher = better recall, slower queries)'
    )
    parser.add_argument(
        '--skip-deployment',
        action='store_true',
        help='Skip index deployment (only create index)'
    )
    parser.add_argument(
        '--deploy-only',
        type=str,
        help='Deploy existing index (provide index resource name)'
    )
    parser.add_argument(
        '--machine-type',
        type=str,
        default='e2-standard-4',
        help='Machine type for serving (e2-standard-16 for 274K vectors)'
    )
    parser.add_argument(
        '--min-replicas',
        type=int,
        default=1,
        help='Minimum number of replicas (2+ for SLA coverage)'
    )
    parser.add_argument(
        '--max-replicas',
        type=int,
        default=1,
        help='Maximum number of replicas'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config(environment=args.env)
    index_config = config.get_index_config()
    endpoint_config = config.get_endpoint_config()
    
    # Apply CLI overrides (CLI args take precedence over config)
    project_id = args.project_id or index_config['project_id']
    location = args.location or index_config['location']
    bucket_name = args.bucket_name or index_config['bucket_name']
    embeddings_prefix = args.embeddings_prefix or index_config['embeddings_prefix']
    index_display_name = args.index_display_name or index_config['display_name']
    endpoint_display_name = args.endpoint_display_name or endpoint_config['display_name']
    algorithm = args.algorithm or index_config['algorithm']
    approximate_neighbors_count = args.approximate_neighbors_count or index_config['approximate_neighbors_count']
    machine_type = args.machine_type or endpoint_config['machine_type']
    min_replicas = args.min_replicas or endpoint_config['min_replicas']
    max_replicas = args.max_replicas or endpoint_config['max_replicas']
    
    print(f"\n{'='*80}")
    print(f"Configuration Loaded")
    print(f"{'='*80}")
    print(f"Environment: {config.environment}")
    print(f"Project ID: {project_id}")
    print(f"Location: {location}")
    print(f"Index: {index_display_name}")
    print(f"Algorithm: {algorithm}")
    print(f"{'='*80}\n")
    
    if args.deploy_only:
        # Deploy existing index
        endpoint = deploy_index(
            project_id=project_id,
            location=location,
            index_name=args.deploy_only,
            endpoint_display_name=endpoint_display_name,
            machine_type=machine_type,
            min_replicas=min_replicas,
            max_replicas=max_replicas
        )
    else:
        # Create index
        index = create_index(
            project_id=project_id,
            location=location,
            bucket_name=bucket_name,
            embeddings_prefix=embeddings_prefix,
            display_name=index_display_name,
            algorithm=algorithm,
            approximate_neighbors_count=approximate_neighbors_count
        )
        
        # Deploy index (unless skipped)
        if not args.skip_deployment:
            endpoint = deploy_index(
                project_id=project_id,
                location=location,
                index_name=index.resource_name,
                endpoint_display_name=endpoint_display_name,
                machine_type=machine_type,
                min_replicas=min_replicas,
                max_replicas=max_replicas
            )
        else:
            print(f"\nSkipping deployment. To deploy later, run:")
            print(f"python build_vector_index.py --deploy-only {index.resource_name}")


if __name__ == "__main__":
    main()
