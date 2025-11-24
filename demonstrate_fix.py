#!/usr/bin/env python3
"""
Demonstration script showing how the enhanced migration verification
fixes the issue with site657 asset count not being detected.
"""

def demonstrate_fix():
    print("DEMONSTRATION: Enhanced Migration Verification Fix")
    print("=" * 50)
    
    # Simulate the specific issue mentioned
    old_site_content = """
    ACME Facility Management System
    Site Dashboard - Site657
    =========================
    Total Assets: 1
    Active Users: 3
    Pending Tasks: 0
    Last Updated: 2025-11-21
    """
    
    new_site_content = """
    ACME Facility Management System
    Site Dashboard - Site657
    =========================
    Total Assets: 0
    Active Users: 3
    Pending Tasks: 0
    Last Updated: 2025-11-22
    """
    
    print("OLD SITE CONTENT:")
    print(old_site_content)
    print("\nNEW SITE CONTENT:")
    print(new_site_content)
    
    # This is the key enhancement - detecting numeric differences
    import re
    
    # Extract asset counts using our enhanced pattern matching
    asset_pattern = r'(?:total\s*)?assets?\s*[:\-]?\s*(\d+)'
    
    old_match = re.search(asset_pattern, old_site_content, re.IGNORECASE)
    new_match = re.search(asset_pattern, new_site_content, re.IGNORECASE)
    
    if old_match and new_match:
        old_count = int(old_match.group(1))
        new_count = int(new_match.group(1))
        
        print(f"\nASSET COUNT DETECTION:")
        print(f"Old site asset count: {old_count}")
        print(f"New site asset count: {new_count}")
        
        if old_count > 0 and new_count == 0:
            print("\n🚨 CRITICAL ISSUE DETECTED! 🚨")
            print("Asset count changed from positive value to zero!")
            print("This indicates potential data loss that requires investigation.")
        elif old_count != new_count:
            print(f"\n⚠️  ASSET COUNT CHANGED from {old_count} to {new_count}")
        else:
            print(f"\n✅ Asset count unchanged: {old_count}")
    else:
        print("\n❌ Could not extract asset counts from content")

if __name__ == "__main__":
    demonstrate_fix()