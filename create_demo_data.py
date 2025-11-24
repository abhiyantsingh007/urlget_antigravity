#!/usr/bin/env python3
"""
Demo script to test the migration verification system with sample data
"""
import json
from datetime import datetime

# Create sample OLD website data (Site657 has 1 asset)
old_data = {
    "metadata": {
        "base_url": "https://acme.egalvanic-rnd.com",
        "capture_time": datetime.now().isoformat(),
        "total_api_responses": 2
    },
    "api_responses": [
        {
            "url": "https://acme.egalvanic-rnd.com/api/sites/overview",
            "timestamp": datetime.now().isoformat(),
            "response": {
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 1,
                        "active_sites": 1,
                        "pending_tasks": 0
                    },
                    "All Facilities": {
                        "name": "All Facilities",
                        "total_assets": 2535,
                        "active_sites": 42,
                        "pending_tasks": 15
                    },
                    "London UK": {
                        "name": "London UK",
                        "total_assets": 450,
                        "active_sites": 5
                    }
                }
            }
        },
        {
            "url": "https://acme.egalvanic-rnd.com/api/dashboard/stats",
            "timestamp": datetime.now().isoformat(),
            "response": {
                "total_sites": 42,
                "total_assets": 2535
            }
        }
    ]
}

# Create sample NEW website data (Site657 has 0 assets - CRITICAL!)
new_data = {
    "metadata": {
        "base_url": "https://acme.egalvanic.ai",
        "capture_time": datetime.now().isoformat(),
        "total_api_responses": 2
    },
    "api_responses": [
        {
            "url": "https://acme.egalvanic.ai/api/sites/overview",
            "timestamp": datetime.now().isoformat(),
            "response": {
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 0,  # CRITICAL: Changed from 1 to 0!
                        "active_sites": 1,
                        "pending_tasks": 0
                    },
                    "All Facilities": {
                        "name": "All Facilities",
                        "total_assets": 1048,  # MAJOR: Decreased significantly
                        "active_sites": 42,
                        "pending_tasks": 15
                    },
                    "London UK": {
                        "name": "London UK",
                        "total_assets": 445,  # MINOR: Small change
                        "active_sites": 5
                    }
                }
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/dashboard/stats",
            "timestamp": datetime.now().isoformat(),
            "response": {
                "total_sites": 42,
                "total_assets": 1048
            }
        }
    ]
}

# Save sample data
print("Creating sample data files for demonstration...")
with open("demo_old_capture.json", "w") as f:
    json.dump(old_data, f, indent=2)
print("✓ Created demo_old_capture.json")

with open("demo_new_capture.json", "w") as f:
    json.dump(new_data, f, indent=2)
print("✓ Created demo_new_capture.json")

print("\nNow run the comparison:")
print("python3 automated_migration_comparison.py demo_old_capture.json demo_new_capture.json")
print("\nExpected results:")
print("- Site657: 1 → 0 (CRITICAL)")
print("- All Facilities: 2535 → 1048 (MAJOR)")
print("- London UK: 450 → 445 (MINOR)")
