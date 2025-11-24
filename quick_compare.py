#!/usr/bin/env python3
"""
Quick comparison tool - automatically finds the latest capture directories
"""

import os
import glob
import sys
from smart_migration_comparator import SmartMigrationComparator

def find_latest_captures():
    """Find the two most recent capture directories"""
    # Look for capture directories
    patterns = [
        'complete_captures_*',
        'complete_tab_captures_*',
        'pre_migration_capture_*',
        'migration_verification_*/old_website_data',
        'migration_verification_*/new_website_data'
    ]
    
    all_dirs = []
    for pattern in patterns:
        dirs = glob.glob(pattern)
        all_dirs.extend([d for d in dirs if os.path.isdir(d)])
    
    if len(all_dirs) < 2:
        return None, None
    
    # Sort by modification time
    all_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    return all_dirs[1], all_dirs[0]  # older, newer

def main():
    if len(sys.argv) == 3:
        # User provided both directories
        old_dir = sys.argv[1]
        new_dir = sys.argv[2]
    elif len(sys.argv) == 1:
        # Auto-detect
        print("🔍 Auto-detecting capture directories...")
        old_dir, new_dir = find_latest_captures()
        
        if not old_dir or not new_dir:
            print("\n❌ Could not find capture directories automatically.")
            print("\nUsage:")
            print("  python3 quick_compare.py <old_capture_dir> <new_capture_dir>")
            print("\nOr run capture scripts first:")
            print("  python3 pre_migration_capture.py   # Capture old site")
            print("  python3 post_migration_capture.py  # Capture new site")
            sys.exit(1)
        
        print(f"\n📁 Found captures:")
        print(f"   Old: {old_dir}")
        print(f"   New: {new_dir}")
        print()
        
        response = input("Compare these? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            sys.exit(0)
    else:
        print("Usage: python3 quick_compare.py [<old_capture_dir> <new_capture_dir>]")
        print("\nIf no directories are provided, will auto-detect the latest captures.")
        sys.exit(1)
    
    # Run comparison
    comparator = SmartMigrationComparator(old_dir, new_dir)
    comparator.compare_captures()
    
    print("\n" + "="*80)
    print("✅ Comparison complete!")
    print("="*80)
    print("\n📄 Open smart_migration_report.html in your browser to view results")

if __name__ == "__main__":
    main()
