import json
import os
import difflib
import sys

def load_json_file(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def compare_json_data(old_data, new_data, filename):
    """Compare two JSON data structures and return differences"""
    try:
        # Convert to strings for comparison
        old_str = json.dumps(old_data, indent=2, sort_keys=True, default=str)
        new_str = json.dumps(new_data, indent=2, sort_keys=True, default=str)
        
        if old_str == new_str:
            return None  # No differences
        else:
            # Generate diff
            diff = list(difflib.unified_diff(
                old_str.splitlines(keepends=True),
                new_str.splitlines(keepends=True),
                fromfile=f"BEFORE MIGRATION: {filename}",
                tofile=f"AFTER MIGRATION: {filename}"
            ))
            return diff
            
    except Exception as e:
        return f"Error comparing {filename}: {str(e)}"

def compare_api_responses(old_dir, new_dir):
    """Compare API responses between two capture directories"""
    print(f"Comparing API responses:")
    print(f"  Before migration: {old_dir}")
    print(f"  After migration: {new_dir}")
    print("=" * 60)
    
    # Get API response files from both directories
    old_api_files = [f for f in os.listdir(old_dir) if f.startswith('api_response_') and f.endswith('.json')]
    new_api_files = [f for f in os.listdir(new_dir) if f.startswith('api_response_') and f.endswith('.json')]
    
    # If no api_response files, check for response_ files (from basic capture)
    if not old_api_files:
        old_api_files = [f for f in os.listdir(old_dir) if f.startswith('response_') and f.endswith('.json') and f != 'all_responses.json']
    
    if not new_api_files:
        new_api_files = [f for f in os.listdir(new_dir) if f.startswith('response_') and f.endswith('.json') and f != 'all_responses.json']
    
    # Identify added, removed, and common files
    old_file_set = set(old_api_files)
    new_file_set = set(new_api_files)
    
    added_files = new_file_set - old_file_set
    removed_files = old_file_set - new_file_set
    common_files = old_file_set & new_file_set
    
    results = {
        "summary": {
            "files_added": list(added_files),
            "files_removed": list(removed_files),
            "files_unchanged": [],
            "files_changed": []
        },
        "details": {}
    }
    
    # Report added/removed files
    if added_files:
        print(f"\nNEW API ENDPOINTS (added after migration):")
        for file in added_files:
            print(f"  + {file}")
    
    if removed_files:
        print(f"\nREMOVED API ENDPOINTS (missing after migration):")
        for file in removed_files:
            print(f"  - {file}")
    
    # Compare common files
    if common_files:
        print(f"\nCOMPARING COMMON API ENDPOINTS:")
        for file in common_files:
            print(f"  Checking {file}...", end=" ")
            
            old_file_path = os.path.join(old_dir, file)
            new_file_path = os.path.join(new_dir, file)
            
            old_data = load_json_file(old_file_path)
            new_data = load_json_file(new_file_path)
            
            if old_data is None or new_data is None:
                print("ERROR - Could not load data")
                continue
            
            diff = compare_json_data(old_data, new_data, file)
            
            if diff is None:
                results["summary"]["files_unchanged"].append(file)
                print("NO CHANGES")
            elif isinstance(diff, list) and len(diff) > 0:
                results["summary"]["files_changed"].append(file)
                results["details"][file] = diff
                print("CHANGED")
            else:
                results["summary"]["files_unchanged"].append(file)
                print("NO CHANGES")
    
    # Summary
    print("\n" + "=" * 60)
    print("API COMPARISON SUMMARY:")
    print(f"  New endpoints: {len(added_files)}")
    print(f"  Removed endpoints: {len(removed_files)}")
    print(f"  Unchanged endpoints: {len(results['summary']['files_unchanged'])}")
    print(f"  Changed endpoints: {len(results['summary']['files_changed'])}")
    
    return results

def main():
    """Main function to compare data captures"""
    if len(sys.argv) != 3:
        print("Usage: python compare_direct.py <before_migration_dir> <after_migration_dir>")
        print("Example: python compare_direct.py api_captures_20251121_195757 complete_captures_20251121_195939")
        sys.exit(1)
    
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    
    # Validate directories
    if not os.path.exists(old_dir):
        print(f"Error: BEFORE migration directory does not exist: {old_dir}")
        sys.exit(1)
    
    if not os.path.exists(new_dir):
        print(f"Error: AFTER migration directory does not exist: {new_dir}")
        sys.exit(1)
    
    # Perform comparison
    print(f"Comparing data between:")
    print(f"  BEFORE: {old_dir}")
    print(f"  AFTER:  {new_dir}")
    
    try:
        results = compare_api_responses(old_dir, new_dir)
        
        # Save detailed results
        results_file = os.path.join(new_dir, "migration_comparison_report.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save human-readable diff report
        diff_report_file = os.path.join(new_dir, "migration_differences.txt")
        with open(diff_report_file, 'w') as f:
            f.write("ACME API MIGRATION COMPARISON REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Before migration data: {old_dir}\n")
            f.write(f"After migration data: {new_dir}\n")
            f.write("=" * 50 + "\n\n")
            
            if results["summary"]["files_added"]:
                f.write("NEWLY ADDED API ENDPOINTS:\n")
                for file in results["summary"]["files_added"]:
                    f.write(f"  + {file}\n")
                f.write("\n")
            
            if results["summary"]["files_removed"]:
                f.write("REMOVED API ENDPOINTS:\n")
                for file in results["summary"]["files_removed"]:
                    f.write(f"  - {file}\n")
                f.write("\n")
            
            if results["summary"]["files_changed"]:
                f.write("CHANGED API ENDPOINTS WITH DIFFERENCES:\n")
                for file in results["summary"]["files_changed"]:
                    f.write(f"\n--- {file} ---\n")
                    if file in results["details"] and isinstance(results["details"][file], list):
                        f.write("".join(results["details"][file]))
                f.write("\n")
        
        print(f"\nDetailed comparison report saved to: {results_file}")
        print(f"Human-readable diff report saved to: {diff_report_file}")
        print(f"\nComparison completed successfully!")
        
    except Exception as e:
        print(f"Error during comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()