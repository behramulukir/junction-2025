#!/usr/bin/env python3
"""
Quick index build and deploy script - runs async without waiting
"""

from google.cloud import aiplatform
import sys

PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "europe-west1"
INDEX_ID = "9119076761890455552"
ENDPOINT_ID = "911842585100681216"

def deploy_to_existing_endpoint():
    """Deploy the newly created index to the existing endpoint."""
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    
    print(f"\n{'='*80}")
    print("DEPLOYING INDEX TO ENDPOINT")
    print(f"{'='*80}")
    
    try:
        # Get the index and endpoint
        index = aiplatform.MatchingEngineIndex(
            f"projects/428461461446/locations/{LOCATION}/indexes/{INDEX_ID}"
        )
        endpoint = aiplatform.MatchingEngineIndexEndpoint(
            f"projects/428461461446/locations/{LOCATION}/indexEndpoints/{ENDPOINT_ID}"
        )
        
        print(f"Index: {index.display_name}")
        print(f"Endpoint: {endpoint.display_name}")
        print(f"\nStarting deployment (this takes ~20-30 minutes)...")
        print(f"  Machine type: n1-standard-16")
        print(f"  Replicas: 2")
        print(f"  Deployed index ID: eu_legislation_test")
        
        # Deploy without waiting
        endpoint.deploy_index(
            index=index,
            deployed_index_id="eu_legislation_test",
            machine_type="n1-standard-16",
            min_replica_count=2,
            max_replica_count=2,
            enable_access_logging=True,
        )
        
        print(f"\n{'='*80}")
        print("✅ DEPLOYMENT STARTED!")
        print(f"{'='*80}")
        print(f"\nMonitor progress with:")
        print(f"  ./monitor_build.sh")
        print(f"\nOr check status:")
        print(f"  python check_deployment.py --endpoint-id {ENDPOINT_ID} --wait")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy_to_existing_endpoint()
