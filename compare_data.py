import json
import os
import difflib
from pathlib import Path

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

def compare_complete_captures(old_dir, new_dir):
    """Compare complete captures between two directories"""
    print(f"Comparing complete captures:")
    print(f"  Before migration: {old_dir}")
    print(f"  After migration: {new_dir}")
    print("=" * 60)
    
    # Compare capture summaries
    old_summary = load_json_file(os.path.join(old_dir, "capture_summary.json"))
    new_summary = load_json_file(os.path.join(new_dir, "capture_summary.json"))
    
    if old_summary and new_summary:
        print("\nCAPTURE SUMMARY COMPARISON:")
        diff = compare_json_data(old_summary, new_summary, "capture_summary.json")
        if diff is None:
            print("  Capture summaries are identical")
        elif isinstance(diff, list) and len(diff) > 0:
            print("  Capture summaries have differences:")
            print("".join(diff[:20]))  # Show first 20 lines of diff
            if len(diff) > 20:
                print("  ... (truncated)")
        else:
            print(f"  {diff}")
    
    # Compare API responses
    api_results = compare_api_responses(old_dir, new_dir)
    
    # Save detailed results
    results_file = os.path.join(new_dir, "migration_comparison_report.json")
    with open(results_file, 'w') as f:
        json.dump(api_results, f, indent=2, default=str)
    
    # Save human-readable diff report
    diff_report_file = os.path.join(new_dir, "migration_differences.txt")
    with open(diff_report_file, 'w') as f:
        f.write("ACME API MIGRATION COMPARISON REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Before migration data: {old_dir}\n")
        f.write(f"After migration data: {new_dir}\n")
        f.write("=" * 50 + "\n\n")
        
        if api_results["summary"]["files_added"]:
            f.write("NEWLY ADDED API ENDPOINTS:\n")
            for file in api_results["summary"]["files_added"]:
                f.write(f"  + {file}\n")
            f.write("\n")
        
        if api_results["summary"]["files_removed"]:
            f.write("REMOVED API ENDPOINTS:\n")
            for file in api_results["summary"]["files_removed"]:
                f.write(f"  - {file}\n")
            f.write("\n")
        
        if api_results["summary"]["files_changed"]:
            f.write("CHANGED API ENDPOINTS WITH DIFFERENCES:\n")
            for file in api_results["summary"]["files_changed"]:
                f.write(f"\n--- {file} ---\n")
                if file in api_results["details"] and isinstance(api_results["details"][file], list):
                    f.write("".join(api_results["details"][file]))
            f.write("\n")
    
    print(f"\nDetailed comparison report saved to: {results_file}")
    print(f"Human-readable diff report saved to: {diff_report_file}")
    
    return api_results

def main():
    """Main function to compare data captures"""
    print("ACME API Migration Comparison Tool")
    print("=" * 40)
    
    # List available capture directories
    capture_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and (d.startswith('api_captures_') or d.startswith('complete_captures_'))]
    
    if not capture_dirs:
        print("No capture directories found in current location.")
        old_dir = input("Enter path to BEFORE migration capture directory: ").strip()
        new_dir = input("Enter path to AFTER migration capture directory: ").strip()
    else:
        print("\nAvailable capture directories:")
        for i, dir_name in enumerate(capture_dirs, 1):
            print(f"  {i}. {dir_name}")
        
        print("\nSelect directories for comparison:")
        try:
            old_idx = int(input("Enter number for BEFORE migration data: ")) - 1
            new_idx = int(input("Enter number for AFTER migration data: ")) - 1
            
            if 0 <= old_idx < len(capture_dirs) and 0 <= new_idx < len(capture_dirs):
                old_dir = capture_dirs[old_idx]
                new_dir = capture_dirs[new_idx]
            else:
                print("Invalid selection. Using manual input.")
                old_dir = input("Enter path to BEFORE migration capture directory: ").strip()
                new_dir = input("Enter path to AFTER migration capture directory: ").strip()
        except ValueError:
            print("Invalid input. Using manual input.")
            old_dir = input("Enter path to BEFORE migration capture directory: ").strip()
            new_dir = input("Enter path to AFTER migration capture directory: ").strip()
    
    # Validate directories
    if not os.path.exists(old_dir):
        print(f"Error: BEFORE migration directory does not exist: {old_dir}")
        return
    
    if not os.path.exists(new_dir):
        print(f"Error: AFTER migration directory does not exist: {new_dir}")
        return
    
    # Perform comparison
    print(f"\nComparing data between:")
    print(f"  BEFORE: {old_dir}")
    print(f"  AFTER:  {new_dir}")
    
    try:
        results = compare_complete_captures(old_dir, new_dir)
        print(f"\nComparison completed successfully!")
        print(f"Check the reports in the {new_dir} directory for details.")
    except Exception as e:
        print(f"Error during comparison: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()