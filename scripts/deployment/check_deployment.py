#!/usr/bin/env python3
"""
Check the status of Vector Search index deployment
"""

from google.cloud import aiplatform
import argparse
import time

PROJECT_ID = "nimble-granite-478311-u2"
LOCATION = "europe-west1"


def check_endpoint_status(endpoint_id: str, project_id: str, location: str):
    """Check if index is deployed and ready."""
    aiplatform.init(project=project_id, location=location)
    
    # Build proper resource name
    if endpoint_id.startswith('projects/'):
        endpoint_resource = endpoint_id
    else:
        endpoint_resource = f"projects/{project_id}/locations/{location}/indexEndpoints/{endpoint_id}"
    
    try:
        endpoint = aiplatform.MatchingEngineIndexEndpoint(endpoint_resource)
        
        print(f"Endpoint: {endpoint.display_name}")
        print(f"Resource: {endpoint.resource_name}")
        print(f"Public Domain: {endpoint.public_endpoint_domain_name}")
        print(f"\nDeployed Indexes:")
        
        if not endpoint.deployed_indexes:
            print("  ❌ No indexes deployed yet")
            print("  ⏳ Deployment may still be in progress...")
            return False
        
        for deployed_idx in endpoint.deployed_indexes:
            print(f"\n  ✅ {deployed_idx.id}")
            print(f"     Index: {deployed_idx.index}")
            print(f"     Machine Type: {deployed_idx.dedicated_resources.machine_spec.machine_type}")
            print(f"     Min Replicas: {deployed_idx.dedicated_resources.min_replica_count}")
            print(f"     Max Replicas: {deployed_idx.dedicated_resources.max_replica_count}")
            
            if deployed_idx.index_sync_time:
                print(f"     ✅ Synced at: {deployed_idx.index_sync_time}")
                print(f"     🟢 READY FOR QUERIES")
                return True
            else:
                print(f"     ⏳ Still syncing...")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def wait_for_deployment(endpoint_id: str, project_id: str, location: str, max_wait_minutes: int = 60):
    """Wait for deployment to complete."""
    print(f"Waiting for deployment (max {max_wait_minutes} minutes)...\n")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    check_interval = 30  # Check every 30 seconds
    
    while time.time() - start_time < max_wait_seconds:
        is_ready = check_endpoint_status(endpoint_id, project_id, location)
        
        if is_ready:
            elapsed = (time.time() - start_time) / 60
            print(f"\n✅ Deployment complete in {elapsed:.1f} minutes!")
            return True
        
        elapsed = (time.time() - start_time) / 60
        remaining = max_wait_minutes - elapsed
        print(f"\n⏳ Still deploying... ({elapsed:.1f}/{max_wait_minutes} min, {remaining:.1f} min remaining)")
        print(f"   Next check in {check_interval}s...\n")
        time.sleep(check_interval)
    
    print(f"\n⚠️  Timeout after {max_wait_minutes} minutes")
    print("   Deployment may still be in progress. Check again later.")
    return False


def main():
    parser = argparse.ArgumentParser(description='Check Vector Search deployment status')
    parser.add_argument('--endpoint-id', type=str, required=True, help='Endpoint ID (e.g., 911842585100681216)')
    parser.add_argument('--project-id', type=str, default=PROJECT_ID, help='GCP project ID')
    parser.add_argument('--location', type=str, default=LOCATION, help='GCP region')
    parser.add_argument('--wait', action='store_true', help='Wait for deployment to complete')
    parser.add_argument('--max-wait', type=int, default=60, help='Max wait time in minutes')
    
    args = parser.parse_args()
    
    if args.wait:
        wait_for_deployment(args.endpoint_id, args.project_id, args.location, args.max_wait)
    else:
        check_endpoint_status(args.endpoint_id, args.project_id, args.location)


if __name__ == "__main__":
    main()
