import json
import os
import difflib
import sys
from pathlib import Path

def load_json_file(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def extract_api_data(response_data):
    """Extract the actual API response data from captured response"""
    if isinstance(response_data, dict):
        # For basic capture format
        if 'response' in response_data:
            return response_data['response']
        # For complete capture format
        elif 'response' in response_data:
            return response_data['response']
    return response_data

def compare_api_endpoints(old_dir, new_dir):
    """Compare API endpoints by content rather than file names"""
    print(f"Comparing API content between:")
    print(f"  {old_dir}")
    print(f"  {new_dir}")
    print("=" * 60)
    
    # Load all response data from both directories
    old_responses = {}
    new_responses = {}
    
    # Load basic capture responses (response_*.json)
    for filename in os.listdir(old_dir):
        if filename.startswith('response_') and filename.endswith('.json') and filename != 'all_responses.json':
            filepath = os.path.join(old_dir, filename)
            data = load_json_file(filepath)
            if data:
                # Extract URL and actual response data
                url = data.get('url', filename)
                response_data = extract_api_data(data)
                old_responses[url] = response_data
    
    # Load complete capture responses (api_response_*.json and response_*.json)
    for filename in os.listdir(new_dir):
        if (filename.startswith('api_response_') or (filename.startswith('response_') and filename != 'all_responses.json')) and filename.endswith('.json'):
            filepath = os.path.join(new_dir, filename)
            data = load_json_file(filepath)
            if data:
                # Extract URL and actual response data
                url = data.get('url', filename)
                response_data = extract_api_data(data)
                new_responses[url] = response_data
    
    # Compare by URL/content rather than file names
    all_urls = set(old_responses.keys()) | set(new_responses.keys())
    
    results = {
        "summary": {
            "endpoints_added": [],
            "endpoints_removed": [],
            "endpoints_unchanged": [],
            "endpoints_changed": []
        },
        "details": {}
    }
    
    for url in all_urls:
        print(f"  Checking {url}...", end=" ")
        
        old_data = old_responses.get(url)
        new_data = new_responses.get(url)
        
        if old_data is None and new_data is not None:
            results["summary"]["endpoints_added"].append(url)
            print("ADDED")
        elif old_data is not None and new_data is None:
            results["summary"]["endpoints_removed"].append(url)
            print("REMOVED")
        elif old_data is not None and new_data is not None:
            # Compare content
            old_str = json.dumps(old_data, indent=2, sort_keys=True, default=str)
            new_str = json.dumps(new_data, indent=2, sort_keys=True, default=str)
            
            if old_str == new_str:
                results["summary"]["endpoints_unchanged"].append(url)
                print("NO CHANGE")
            else:
                results["summary"]["endpoints_changed"].append(url)
                # Generate diff
                diff = list(difflib.unified_diff(
                    old_str.splitlines(keepends=True),
                    new_str.splitlines(keepends=True),
                    fromfile=f"BEFORE: {url}",
                    tofile=f"AFTER: {url}"
                ))
                results["details"][url] = diff
                print("CHANGED")
    
    # Summary
    print("\n" + "=" * 60)
    print("API CONTENT COMPARISON SUMMARY:")
    print(f"  New endpoints: {len(results['summary']['endpoints_added'])}")
    print(f"  Removed endpoints: {len(results['summary']['endpoints_removed'])}")
    print(f"  Unchanged endpoints: {len(results['summary']['endpoints_unchanged'])}")
    print(f"  Changed endpoints: {len(results['summary']['endpoints_changed'])}")
    
    return results

def main():
    """Main function to compare API content"""
    if len(sys.argv) != 3:
        print("Usage: python compare_content.py <first_capture_dir> <second_capture_dir>")
        print("Example: python compare_content.py api_captures_20251121_200411 complete_captures_20251121_200510")
        sys.exit(1)
    
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    
    # Validate directories
    if not os.path.exists(old_dir):
        print(f"Error: First directory does not exist: {old_dir}")
        sys.exit(1)
    
    if not os.path.exists(new_dir):
        print(f"Error: Second directory does not exist: {new_dir}")
        sys.exit(1)
    
    # Perform comparison
    print(f"Comparing API content between:")
    print(f"  First capture: {old_dir}")
    print(f"  Second capture: {new_dir}")
    
    try:
        results = compare_api_endpoints(old_dir, new_dir)
        
        # Save detailed results
        results_file = os.path.join(new_dir, "content_comparison_report.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save human-readable diff report
        diff_report_file = os.path.join(new_dir, "content_differences.txt")
        with open(diff_report_file, 'w') as f:
            f.write("ACME API CONTENT COMPARISON REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"First capture: {old_dir}\n")
            f.write(f"Second capture: {new_dir}\n")
            f.write("=" * 50 + "\n\n")
            
            if results["summary"]["endpoints_added"]:
                f.write("NEWLY ADDED API ENDPOINTS:\n")
                for url in results["summary"]["endpoints_added"]:
                    f.write(f"  + {url}\n")
                f.write("\n")
            
            if results["summary"]["endpoints_removed"]:
                f.write("REMOVED API ENDPOINTS:\n")
                for url in results["summary"]["endpoints_removed"]:
                    f.write(f"  - {url}\n")
                f.write("\n")
            
            if results["summary"]["endpoints_changed"]:
                f.write("CHANGED API ENDPOINTS WITH DIFFERENCES:\n")
                for url in results["summary"]["endpoints_changed"]:
                    f.write(f"\n--- {url} ---\n")
                    if url in results["details"] and isinstance(results["details"][url], list):
                        f.write("".join(results["details"][url]))
                f.write("\n")
            
            if results["summary"]["endpoints_unchanged"]:
                f.write("UNCHANGED API ENDPOINTS:\n")
                for url in results["summary"]["endpoints_unchanged"]:
                    f.write(f"  = {url}\n")
                f.write("\n")
        
        print(f"\nDetailed content comparison report saved to: {results_file}")
        print(f"Human-readable content diff report saved to: {diff_report_file}")
        print(f"\nContent comparison completed successfully!")
        
    except Exception as e:
        print(f"Error during content comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()