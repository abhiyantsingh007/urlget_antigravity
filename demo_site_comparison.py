#!/usr/bin/env python3
"""
DEMO: Site Comparison with Sample Data
Shows the exact table format you want for site comparisons
"""

import json
import os
from site_data_comparator import SiteDataComparator

# Create demo directories
os.makedirs("demo_old_dashboard", exist_ok=True)
os.makedirs("demo_new_dashboard", exist_ok=True)

# OLD site dashboard data - COMPREHENSIVE (all tabs/metrics)
old_dashboard = {
    "api_responses": [{
        "url": "https://example.com/api/dashboard/sites",
        "response": {
            "sites": {
                "Site657": {
                    "name": "Site657",
                    # Assets tab
                    "total_assets": 1,
                    # Issues tab
                    "open_issues": 5,
                    "unresolved_issues": 3,
                    "resolved_issues": 2,
                    # Site Visits tab
                    "active_sessions": 2,
                    "completed_sessions": 10,
                    # Tasks tab
                    "pending_tasks": 3,
                    "completed_tasks": 7,
                    # Opportunities tab
                    "opportunities_value": 50000,
                    "opportunities_count": 2
                },
                "All Facilities": {
                    "name": "All Facilities",
                    # Assets tab
                    "total_assets": 2535,
                    # Issues tab
                    "open_issues": 71,
                    "unresolved_issues": 60,
                    "resolved_issues": 250,
                    # Site Visits tab
                    "active_sessions": 43,
                    "completed_sessions": 120,
                    # Tasks tab
                    "pending_tasks": 144,
                    "completed_tasks": 380,
                    # Opportunities tab
                    "opportunities_value": 485000,
                    "opportunities_count": 25,
                    # Equipment tab
                    "equipment_at_risk": 1200000
                },
                "London UK": {
                    "name": "London UK",
                    # Assets tab
                    "total_assets": 450,
                    # Issues tab
                    "open_issues": 12,
                    "unresolved_issues": 10,
                    "resolved_issues": 45,
                    # Site Visits tab
                    "active_sessions": 8,
                    "completed_sessions": 25,
                    # Tasks tab
                    "pending_tasks": 15,
                    "completed_tasks": 50,
                    # Opportunities tab
                    "opportunities_value": 75000,
                    "opportunities_count": 5
                },
                "Melbourne AU": {
                    "name": "Melbourne AU",
                    # Assets tab
                    "total_assets": 320,
                    # Issues tab
                    "open_issues": 15,
                    "unresolved_issues": 12,
                    "resolved_issues": 30,
                    # Site Visits tab
                    "active_sessions": 5,
                    "completed_sessions": 18,
                    # Tasks tab
                    "pending_tasks": 8,
                    "completed_tasks": 25
                },
                "Toronto Canada": {
                    "name": "Toronto Canada",
                    # Assets tab
                    "total_assets": 275,
                    # Issues tab
                    "open_issues": 8,
                    "unresolved_issues": 6,
                    "resolved_issues": 22,
                    # Site Visits tab
                    "active_sessions": 3,
                    "completed_sessions": 12,
                    # Tasks tab
                    "pending_tasks": 5,
                    "completed_tasks": 18
                }
            }
        }
    }]
}

# NEW site dashboard data - showing changes across ALL tabs
new_dashboard = {
    "api_responses": [{
        "url": "https://example.com/api/dashboard/sites",
        "response": {
            "sites": {
                "Site657": {
                    "name": "Site657",
                    # Assets tab - CRITICAL DATA LOSS
                    "total_assets": 0,  # Lost all assets!
                    # Issues tab
                    "open_issues": 5,
                    "unresolved_issues": 3,
                    "resolved_issues": 2,
                    # Site Visits tab
                    "active_sessions": 2,
                    "completed_sessions": 10,
                    # Tasks tab
                    "pending_tasks": 3,
                    "completed_tasks": 7,
                    # Opportunities tab
                    "opportunities_value": 50000,
                    "opportunities_count": 2
                },
                "All Facilities": {
                    "name": "All Facilities",
                    # Assets tab - MAJOR CHANGE
                    "total_assets": 1048,  # Lost 1487 assets
                    # Issues tab - IMPROVEMENTS
                    "open_issues": 57,  # Reduced from 71
                    "unresolved_issues": 45,  # Reduced from 60
                    "resolved_issues": 275,  # Increased from 250
                    # Site Visits tab - CHANGES
                    "active_sessions": 33,  # Reduced from 43
                    "completed_sessions": 135,  # Increased from 120
                    # Tasks tab - CHANGES
                    "pending_tasks": 129,  # Reduced from 144
                    "completed_tasks": 395,  # Increased from 380
                    # Opportunities tab - MAJOR CHANGE
                    "opportunities_value": 334000,  # Reduced from 485000
                    "opportunities_count": 18,  # Reduced from 25
                    # Equipment tab
                    "equipment_at_risk": 950000  # Reduced from 1200000
                },
                "London UK": {
                    "name": "London UK",
                    # Assets tab - MINOR CHANGE
                    "total_assets": 445,  # Lost 5 assets
                    # Issues tab
                    "open_issues": 12,
                    "unresolved_issues": 10,
                    "resolved_issues": 47,  # Slight increase
                    # Site Visits tab
                    "active_sessions": 8,
                    "completed_sessions": 27,  # Slight increase
                    # Tasks tab
                    "pending_tasks": 15,
                    "completed_tasks": 52,  # Slight increase
                    # Opportunities tab
                    "opportunities_value": 75000,
                    "opportunities_count": 5
                },
                "Melbourne AU": {
                    "name": "Melbourne AU",
                    # Assets tab - NO CHANGE
                    "total_assets": 320,
                    # Issues tab
                    "open_issues": 15,
                    "unresolved_issues": 12,
                    "resolved_issues": 32,  # Slight increase
                    # Site Visits tab
                    "active_sessions": 5,
                    "completed_sessions": 20,  # Slight increase
                    # Tasks tab
                    "pending_tasks": 8,
                    "completed_tasks": 27  # Slight increase
                },
                "Toronto Canada": {
                    "name": "Toronto Canada",
                    # Assets tab - NO CHANGE
                    "total_assets": 275,
                    # Issues tab
                    "open_issues": 8,
                    "unresolved_issues": 6,
                    "resolved_issues": 24,  # Slight increase
                    # Site Visits tab
                    "active_sessions": 3,
                    "completed_sessions": 14,  # Slight increase
                    # Tasks tab
                    "pending_tasks": 5,
                    "completed_tasks": 20  # Slight increase
                }
            }
        }
    }]
}

# Save demo data
with open("demo_old_dashboard/complete_capture.json", "w") as f:
    json.dump(old_dashboard, f, indent=2)

with open("demo_new_dashboard/complete_capture.json", "w") as f:
    json.dump(new_dashboard, f, indent=2)

print("✅ Demo dashboard data created")
print("\n📋 This demo will show:")
print("   🔴 CRITICAL: Site657 lost all assets (1 → 0)")
print("   🟠 MAJOR: All Facilities lost 1,487 assets (2,535 → 1,048)")
print("   🟠 MAJOR: All Facilities issues reduced by 14 (71 → 57)")
print("   🟠 MAJOR: All Facilities sessions reduced by 10 (43 → 33)")
print("   🟡 MINOR: London UK lost 5 assets (450 → 445)")
print("   🟡 MINOR: All Facilities tasks reduced by 15 (144 → 129)")
print("\nRunning comparison...\n")

# Run comparison
comparator = SiteDataComparator("demo_old_dashboard", "demo_new_dashboard")
comparator.compare_sites()

print("\n" + "="*80)
print("✅ Demo complete!")
print("="*80)
print("\n📄 Open site_comparison_report.html to see the table format you asked for")
print("\n💡 To get this for YOUR REAL DATA, you need to:")
print("   1. Capture the main dashboard page that shows all sites")
print("   2. The dashboard should have an API endpoint like /api/dashboard/sites")
print("   3. Or capture each site's overview individually")
