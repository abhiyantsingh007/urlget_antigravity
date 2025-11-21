import json
import os
import difflib
from pathlib import Path

def compare_json_files(file1_path, file2_path):
    """
    Compare two JSON files and return differences
    """
    try:
        with open(file1_path, 'r') as f1:
            data1 = json.load(f1)
        
        with open(file2_path, 'r') as f2:
            data2 = json.load(f2)
        
        # Convert to strings for comparison
        str1 = json.dumps(data1, indent=2, sort_keys=True, default=str)
        str2 = json.dumps(data2, indent=2, sort_keys=True, default=str)
        
        if str1 == str2:
            return None  # No differences
        else:
            # Generate diff
            diff = list(difflib.unified_diff(
                str1.splitlines(keepends=True),
                str2.splitlines(keepends=True),
                fromfile=f"PRE-MIGRATION: {os.path.basename(file1_path)}",
                tofile=f"POST-MIGRATION: {os.path.basename(file2_path)}"
            ))
            return diff
            
    except Exception as e:
        return f"Error comparing files: {str(e)}"

def analyze_api_differences(pre_migration_dir, post_migration_dir):
    """
    Analyze differences between pre and post migration API captures
    """
    print(f"Analyzing differences between:")
    print(f"  Pre-migration: {pre_migration_dir}")
    print(f"  Post-migration: {post_migration_dir}")
    print("=" * 60)
    
    pre_api_dir = os.path.join(pre_migration_dir, "api_responses")
    post_api_dir = os.path.join(post_migration_dir, "api_responses")
    
    # Check if directories exist
    if not os.path.exists(pre_api_dir):
        print(f"Warning: Pre-migration API directory not found: {pre_api_dir}")
        pre_api_dir = pre_migration_dir  # Try root directory
    
    if not os.path.exists(post_api_dir):
        print(f"Warning: Post-migration API directory not found: {post_api_dir}")
        post_api_dir = post_migration_dir  # Try root directory
    
    # Get list of JSON files in both directories
    pre_files = {f for f in os.listdir(pre_api_dir) if f.endswith('.json')}
    post_files = {f for f in os.listdir(post_api_dir) if f.endswith('.json')}
    
    # Identify added, removed, and common files
    added_files = post_files - pre_files
    removed_files = pre_files - post_files
    common_files = pre_files & post_files
    
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
        print(f"\nNEW FILES (added after migration):")
        for file in added_files:
            print(f"  + {file}")
    
    if removed_files:
        print(f"\nREMOVED FILES (missing after migration):")
        for file in removed_files:
            print(f"  - {file}")
    
    # Compare common files
    if common_files:
        print(f"\nCOMPARING COMMON FILES:")
        for file in common_files:
            print(f"  Checking {file}...", end=" ")
            
            pre_file_path = os.path.join(pre_api_dir, file)
            post_file_path = os.path.join(post_api_dir, file)
            
            diff = compare_json_files(pre_file_path, post_file_path)
            
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
    print("SUMMARY:")
    print(f"  Files added: {len(added_files)}")
    print(f"  Files removed: {len(removed_files)}")
    print(f"  Files unchanged: {len(results['summary']['files_unchanged'])}")
    print(f"  Files changed: {len(results['summary']['files_changed'])}")
    
    # Save detailed results
    results_file = os.path.join(post_migration_dir, "migration_comparison_report.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save human-readable diff report
    diff_report_file = os.path.join(post_migration_dir, "migration_differences.txt")
    with open(diff_report_file, 'w') as f:
        f.write("ACME API MIGRATION COMPARISON REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Pre-migration data: {pre_migration_dir}\n")
        f.write(f"Post-migration data: {post_migration_dir}\n")
        f.write("=" * 50 + "\n\n")
        
        if added_files:
            f.write("NEWLY ADDED FILES:\n")
            for file in added_files:
                f.write(f"  + {file}\n")
            f.write("\n")
        
        if removed_files:
            f.write("REMOVED FILES:\n")
            for file in removed_files:
                f.write(f"  - {file}\n")
            f.write("\n")
        
        if results["summary"]["files_changed"]:
            f.write("CHANGED FILES WITH DIFFERENCES:\n")
            for file in results["summary"]["files_changed"]:
                f.write(f"\n--- {file} ---\n")
                if file in results["details"] and isinstance(results["details"][file], list):
                    f.write("".join(results["details"][file]))
            f.write("\n")
    
    print(f"\nDetailed comparison report saved to: {results_file}")
    print(f"Human-readable diff report saved to: {diff_report_file}")
    
    return results

def interactive_comparison():
    """
    Interactive mode to select directories for comparison
    """
    print("ACME API Migration Comparison Tool")
    print("=" * 40)
    
    # List available capture directories
    capture_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and (d.startswith('api_captures_') or d.startswith('captured_data_'))]
    
    if not capture_dirs:
        print("No capture directories found in current location.")
        pre_dir = input("Enter path to pre-migration capture directory: ").strip()
        post_dir = input("Enter path to post-migration capture directory: ").strip()
    else:
        print("\nAvailable capture directories:")
        for i, dir_name in enumerate(capture_dirs, 1):
            print(f"  {i}. {dir_name}")
        
        print("\nSelect directories for comparison:")
        try:
            pre_idx = int(input("Enter number for PRE-migration data: ")) - 1
            post_idx = int(input("Enter number for POST-migration data: ")) - 1
            
            if 0 <= pre_idx < len(capture_dirs) and 0 <= post_idx < len(capture_dirs):
                pre_dir = capture_dirs[pre_idx]
                post_dir = capture_dirs[post_idx]
            else:
                print("Invalid selection. Using manual input.")
                pre_dir = input("Enter path to pre-migration capture directory: ").strip()
                post_dir = input("Enter path to post-migration capture directory: ").strip()
        except ValueError:
            print("Invalid input. Using manual input.")
            pre_dir = input("Enter path to pre-migration capture directory: ").strip()
            post_dir = input("Enter path to post-migration capture directory: ").strip()
    
    # Perform comparison
    if os.path.exists(pre_dir) and os.path.exists(post_dir):
        return analyze_api_differences(pre_dir, post_dir)
    else:
        print("Error: One or both directories do not exist.")
        return None

if __name__ == "__main__":
    # Try interactive mode first
    try:
        result = interactive_comparison()
        if result is None:
            print("\nExample usage:")
            print("analyze_api_differences('api_captures_20231121_100000', 'api_captures_20231122_150000')")
    except KeyboardInterrupt:
        print("\nComparison cancelled by user.")
    except Exception as e:
        print(f"Error during comparison: {str(e)}")