"""
Script to run post-migration data capture and compare with pre-migration data
"""

import os
from post_migration_capture import PostMigrationDataCapture
from pre_migration_capture import compare_pre_post_migration

# Configuration - Update with actual credentials
BASE_URL = "https://acme.egalvanic.ai"  # Update if URL changes after migration
EMAIL = "rahul+acme@egalvanic.com"
PASSWORD = "RP@egalvanic123"

def find_latest_pre_migration_capture():
    """Find the most recent pre-migration capture directory"""
    captures = [d for d in os.listdir('.') if d.startswith('pre_migration_capture_') and os.path.isdir(d)]
    if not captures:
        return None
    # Return the most recently created directory
    return sorted(captures)[-1]

if __name__ == "__main__":
    # Run post-migration capture
    capture = PostMigrationDataCapture(BASE_URL, EMAIL, PASSWORD)
    post_capture_dir = capture.run_capture()
    
    print(f"\nPost-migration capture completed!")
    print(f"All data has been saved to: {post_capture_dir}")
    
    # Find the latest pre-migration capture for comparison
    pre_capture_dir = find_latest_pre_migration_capture()
    
    if pre_capture_dir:
        print(f"\nFound pre-migration capture: {pre_capture_dir}")
        print("Running comparison...")
        
        # Compare pre and post migration data
        compare_pre_post_migration(pre_capture_dir, post_capture_dir)
    else:
        print("\nNo pre-migration capture found!")
        print("Please run the pre-migration capture first, then run this script after migration.")
        print("\nTo manually compare later, use:")
        print("compare_pre_post_migration('path_to_pre_capture', '{post_capture_dir}')")