#!/usr/bin/env python3
"""Debug script to test analysis endpoint and see raw LLM output"""

import requests
import json

# Test the deployed backend
url = "https://eu-legislation-api-428461461446.europe-west1.run.app/api/analyze"

payload = {
    "subcategory_id": "1.1",
    "subcategory_description": "Credit risk assessment and capital requirements for banking institutions",
    "top_k": 10
}

print("Testing analysis endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...\n")

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
print(json.dumps(response.json(), indent=2))

# Also test with a different query
print("\n" + "="*80)
print("Testing with different query...")
print("="*80 + "\n")

payload2 = {
    "subcategory_id": "2.1",
    "subcategory_description": "Market risk capital requirements including value at risk models",
    "top_k": 15
}

response2 = requests.post(url, json=payload2)
print(f"Status Code: {response2.status_code}")
print(f"\nResponse:")
print(json.dumps(response2.json(), indent=2))
