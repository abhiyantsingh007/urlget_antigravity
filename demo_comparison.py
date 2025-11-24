"""
Demo script to show how the comparison between pre and post migration data would work
"""

import json
import os

def demo_comparison():
    """Demonstrate how the comparison between pre and post migration data works"""
    
    print("DEMO: Pre vs Post Migration Data Comparison")
    print("="*50)
    
    # Simulate pre-migration data (from our demo capture)
    pre_migration_data = [
        {
            "url": "https://acme.egalvanic.ai/api/dashboard/stats",
            "status": 200,
            "response": {
                "total_sites": 42,
                "active_users": 127,
                "pending_issues": 5,
                "completed_tasks": 203
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/sites",
            "status": 200,
            "response": {
                "sites": [
                    {"id": 1, "name": "Site A", "status": "active"},
                    {"id": 2, "name": "Site B", "status": "maintenance"},
                    {"id": 3, "name": "Site C", "status": "active"}
                ]
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/profile",
            "status": 200,
            "response": {
                "user_id": 1001,
                "name": "Rahul Patel",
                "email": "rahul@egalvanic.com",
                "role": "administrator"
            }
        }
    ]
    
    # Simulate post-migration data (with some changes)
    post_migration_data = [
        {
            "url": "https://acme.egalvanic.ai/api/dashboard/stats",
            "status": 200,
            "response": {
                "total_sites": 42,  # Same
                "active_users": 129,  # Changed from 127
                "pending_issues": 5,  # Same
                "completed_tasks": 203  # Same
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/sites",
            "status": 200,
            "response": {
                "sites": [
                    {"id": 1, "name": "Site A", "status": "active"},
                    {"id": 2, "name": "Site B", "status": "maintenance"},
                    {"id": 3, "name": "Site C", "status": "active"},
                    {"id": 4, "name": "Site D", "status": "active"}  # New site added
                ]
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/profile",
            "status": 200,
            "response": {
                "user_id": 1001,
                "name": "Rahul Patel",
                "email": "rahul@egalvanic.com",
                "role": "administrator"
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/new-feature",  # New API endpoint
            "status": 200,
            "response": {
                "feature_enabled": True,
                "version": "2.0"
            }
        }
    ]
    
    print("Comparing pre-migration and post-migration API responses...\n")
    
    # Compare responses
    pre_urls = {item["url"]: item["response"] for item in pre_migration_data}
    post_urls = {item["url"]: item["response"] for item in post_migration_data}
    
    # Find differences
    matching = 0
    different = 0
    missing = []
    added = []
    
    # Check for missing URLs
    for url in pre_urls:
        if url not in post_urls:
            missing.append(url)
        else:
            # Compare responses
            if pre_urls[url] == post_urls[url]:
                matching += 1
            else:
                different += 1
                print(f"DIFFERENCE FOUND in {url}:")
                print(f"  Pre:  {pre_urls[url]}")
                print(f"  Post: {post_urls[url]}\n")
    
    # Check for added URLs
    for url in post_urls:
        if url not in pre_urls:
            added.append(url)
    
    # Results
    print("COMPARISON RESULTS:")
    print("="*30)
    print(f"Matching responses: {matching}")
    print(f"Different responses: {different}")
    print(f"Missing responses: {len(missing)}")
    print(f"Added responses: {len(added)}")
    
    if missing:
        print("\nMISSING API ENDPOINTS:")
        for url in missing:
            print(f"  - {url}")
    
    if added:
        print("\nNEW API ENDPOINTS:")
        for url in added:
            print(f"  + {url}")
            print(f"    Response: {post_urls[url]}")

if __name__ == "__main__":
    demo_comparison()