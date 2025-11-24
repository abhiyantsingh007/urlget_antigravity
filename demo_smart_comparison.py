#!/usr/bin/env python3
"""
Create demo data showing different types of comparison results
"""

import json
import os
from smart_migration_comparator import SmartMigrationComparator

# Create demo directories
os.makedirs("demo_old_site", exist_ok=True)
os.makedirs("demo_new_site", exist_ok=True)

# Old site data
old_data = {
    "api_responses": [
        {
            "url": "https://example.com/api/sites/overview",
            "response": {
                "timestamp": "2024-01-01T10:00:00Z",  # Will be ignored
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 25,  # Will become 0 - CRITICAL!
                        "active_sessions_count": 5,
                        "open_issues_count": 3
                    },
                    "MainFacility": {
                        "name": "MainFacility", 
                        "total_assets": 2500,  # Will change to 1500 - MAJOR!
                        "active_sessions_count": 42,
                        "open_issues_count": 15
                    },
                    "SmallSite": {
                        "name": "SmallSite",
                        "total_assets": 10,  # No change
                        "active_sessions_count": 2,
                        "open_issues_count": 1
                    }
                },
                "session_id": "old-session-123",  # Will be ignored
                "access_token": "eyJhbGci0iJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Will be ignored
            }
        },
        {
            "url": "https://example.com/api/assets/list",
            "response": {
                "timestamp": "2024-01-01T10:01:00Z",  # Will be ignored
                "assets": [
                    {
                        "id": "asset-001",
                        "name": "Transformer A",
                        "status": "operational",
                        "voltage": 480
                    },
                    {
                        "id": "asset-002", 
                        "name": "Panel B",
                        "status": "maintenance",  # Will change to "operational"
                        "voltage": 208
                    }
                ]
            }
        },
        {
            "url": "https://example.com/api/user/preferences",
            "response": {
                "timestamp": "2024-01-01T10:02:00Z",  # Will be ignored
                "user_id": "user-123",
                "theme": "light",  # Will change to "dark" - MINOR
                "notifications_enabled": True
            }
        }
    ]
}

# New site data - with some changes
new_data = {
    "api_responses": [
        {
            "url": "https://example.com/api/sites/overview",
            "response": {
                "timestamp": "2024-01-15T14:30:00Z",  # Different timestamp - IGNORED
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 0,  # DATA LOSS! Was 25
                        "active_sessions_count": 5,
                        "open_issues_count": 3
                    },
                    "MainFacility": {
                        "name": "MainFacility",
                        "total_assets": 1500,  # Large drop! Was 2500
                        "active_sessions_count": 42,
                        "open_issues_count": 8  # Some issues fixed
                    },
                    "SmallSite": {
                        "name": "SmallSite",
                        "total_assets": 10,  # Unchanged
                        "active_sessions_count": 2,
                        "open_issues_count": 1
                    }
                },
                "session_id": "new-session-789",  # Different session - IGNORED
                "access_token": "eyJhbGci0iJSUzI1NiIsInR5cCI6IkpXVCJ9..."  # Different token - IGNORED
            }
        },
        {
            "url": "https://example.com/api/assets/list",
            "response": {
                "timestamp": "2024-01-15T14:31:00Z",  # Different timestamp - IGNORED
                "assets": [
                    {
                        "id": "asset-001",
                        "name": "Transformer A",
                        "status": "operational",
                        "voltage": 480
                    },
                    {
                        "id": "asset-002",
                        "name": "Panel B", 
                        "status": "operational",  # Changed from "maintenance"
                        "voltage": 208
                    }
                ]
            }
        },
        {
            "url": "https://example.com/api/user/preferences",
            "response": {
                "timestamp": "2024-01-15T14:32:00Z",  # Different timestamp - IGNORED
                "user_id": "user-123",
                "theme": "dark",  # Changed from "light"
                "notifications_enabled": True
            }
        }
    ]
}

# Save demo data
with open("demo_old_site/complete_capture.json", "w") as f:
    json.dump(old_data, f, indent=2)

with open("demo_new_site/complete_capture.json", "w") as f:
    json.dump(new_data, f, indent=2)

print("✅ Demo data created in demo_old_site/ and demo_new_site/")
print("\n📋 This demo includes:")
print("   🔴 CRITICAL: Site657 lost all assets (25 → 0)")
print("   🟠 MAJOR: MainFacility lost 1000 assets (2500 → 1500)")
print("   🟠 MAJOR: MainFacility issues reduced (15 → 8)")
print("   🟡 MINOR: Panel B status changed (maintenance → operational)")
print("   🟡 MINOR: User theme changed (light → dark)")
print("   ✅ IGNORED: Timestamps, session IDs, tokens all changed (as expected)")
print("\nRunning comparison...\n")

# Run comparison
comparator = SmartMigrationComparator("demo_old_site", "demo_new_site")
comparator.compare_captures()

print("\n" + "="*80)
print("✅ Demo comparison complete!")
print("="*80)
print("\n📄 Open smart_migration_report.html in your browser to see:")
print("   - What CRITICAL, MAJOR, and MINOR differences look like")
print("   - How ignored fields don't clutter the report")
print("   - How the same data shows as IDENTICAL even with different timestamps")
