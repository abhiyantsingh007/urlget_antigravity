#!/usr/bin/env python3
"""
BATCH JSON COMPARATOR
Automates comparison of multiple JSON files and directories
"""

import json
import os
import sys
import glob
from datetime import datetime
from comprehensive_json_comparator import ComprehensiveJSONComparator

def find_json_files(directory, pattern="*.json"):
    """Find all JSON files in a directory"""
    full_pattern = os.path.join(directory, "**", pattern)
    return sorted(glob.glob(full_pattern, recursive=True))

def find_capture_files(base_path):
    """Find complete_capture.json files in base path"""
    pattern = os.path.join(base_path, "**/complete_capture.json")
    return sorted(glob.glob(pattern, recursive=True))

def compare_consecutive_captures(base_directory, output_dir="batch_comparisons"):
    """Compare consecutive capture directories"""
    capture_dirs = sorted(glob.glob(os.path.join(base_directory, "complete_captures_*")))
    
    if len(capture_dirs) < 2:
        print(f"Found only {len(capture_dirs)} capture directories. Need at least 2.")
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    print(f"Found {len(capture_dirs)} capture directories\n")
    
    for i in range(len(capture_dirs) - 1):
        old_dir = capture_dirs[i]
        new_dir = capture_dirs[i + 1]
        
        old_file = os.path.join(old_dir, "complete_capture.json")
        new_file = os.path.join(new_dir, "complete_capture.json")
        
        if not os.path.exists(old_file) or not os.path.exists(new_file):
            print(f"⚠️  Skipping: Missing complete_capture.json files")
            continue
        
        # Extract timestamps from directory names
        old_name = os.path.basename(old_dir)
        new_name = os.path.basename(new_dir)
        
        output_name = os.path.join(output_dir, f"comparison_{i+1}_to_{i+2}")
        
        print(f"\n[{i+1}/{len(capture_dirs)-1}] Comparing captures...")
        print(f"  Old: {old_name}")
        print(f"  New: {new_name}")
        
        try:
            comparator = ComprehensiveJSONComparator(old_file, new_file, output_name)
            
            if comparator.compare():
                comparator.generate_html_report()
                comparator.generate_json_report()
                
                results.append({
                    "comparison": f"{i+1} → {i+2}",
                    "old_dir": old_name,
                    "new_dir": new_name,
                    "statistics": comparator.statistics,
                    "reports": {
                        "html": f"{output_name}.html",
                        "json": f"{output_name}.json"
                    }
                })
                
                print(f"  ✅ Success")
                print(f"     - Critical: {comparator.statistics['critical']}")
                print(f"     - Major: {comparator.statistics['major']}")
                print(f"     - Minor: {comparator.statistics['minor']}")
            else:
                print(f"  ❌ Failed to compare")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    return results

def compare_directory_pair(old_dir, new_dir, output_name="directory_comparison"):
    """Compare JSON files within two directories"""
    # Find all JSON files
    old_files = find_json_files(old_dir)
    new_files = find_json_files(new_dir)
    
    # Create output directory
    output_dir = "directory_comparisons"
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    print(f"Found {len(old_files)} JSON files in old directory")
    print(f"Found {len(new_files)} JSON files in new directory\n")
    
    # Compare by filename
    old_by_name = {os.path.basename(f): f for f in old_files}
    new_by_name = {os.path.basename(f): f for f in new_files}
    
    all_names = set(old_by_name.keys()) | set(new_by_name.keys())
    
    for idx, filename in enumerate(sorted(all_names), 1):
        old_file = old_by_name.get(filename)
        new_file = new_by_name.get(filename)
        
        if old_file and new_file:
            print(f"\n[{idx}] Comparing {filename}...")
            
            try:
                comp_name = os.path.join(output_dir, f"comp_{idx}_{filename.replace('.json', '')}")
                comparator = ComprehensiveJSONComparator(old_file, new_file, comp_name)
                
                if comparator.compare():
                    comparator.generate_html_report()
                    comparator.generate_json_report()
                    
                    results.append({
                        "file": filename,
                        "statistics": comparator.statistics,
                        "reports": {
                            "html": f"{comp_name}.html",
                            "json": f"{comp_name}.json"
                        }
                    })
                    
                    print(f"  ✅ {comparator.statistics['differences_found']} differences found")
                else:
                    print(f"  ❌ Failed")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        elif old_file:
            print(f"\n[{idx}] ⚠️  {filename} only in old directory")
        elif new_file:
            print(f"\n[{idx}] ⚠️  {filename} only in new directory")
    
    return results

def generate_batch_summary(results, output_file="batch_summary.html"):
    """Generate summary HTML of all comparisons"""
    
    total_comparisons = len(results)
    total_differences = sum(r["statistics"]["differences_found"] for r in results)
    total_critical = sum(r["statistics"]["critical"] for r in results)
    total_major = sum(r["statistics"]["major"] for r in results)
    total_minor = sum(r["statistics"]["minor"] for r in results)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Batch Comparison Summary</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 5px solid #ddd;
        }}
        .summary-card.critical {{ border-left-color: #e74c3c; }}
        .summary-card.major {{ border-left-color: #f39c12; }}
        .summary-card.minor {{ border-left-color: #3498db; }}
        .summary-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .summary-card.critical .summary-number {{ color: #e74c3c; }}
        .summary-card.major .summary-number {{ color: #f39c12; }}
        .summary-card.minor .summary-number {{ color: #3498db; }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }}
        .table td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        .table tr:hover {{ background: #f8f9fa; }}
        .link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Batch Comparison Summary</h1>
            <p>Overview of all JSON comparisons</p>
            <p style="font-size: 12px; opacity: 0.9;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-number">{total_comparisons}</div>
                <div>Total Comparisons</div>
            </div>
            <div class="summary-card">
                <div class="summary-number">{total_differences}</div>
                <div>Total Differences</div>
            </div>
            <div class="summary-card critical">
                <div class="summary-number">{total_critical}</div>
                <div>Critical Issues</div>
            </div>
            <div class="summary-card major">
                <div class="summary-number">{total_major}</div>
                <div>Major Changes</div>
            </div>
            <div class="summary-card minor">
                <div class="summary-number">{total_minor}</div>
                <div>Minor Changes</div>
            </div>
        </div>
        
        <table class="table">
            <thead>
                <tr>
                    <th>Comparison</th>
                    <th>Total Differences</th>
                    <th>Critical</th>
                    <th>Major</th>
                    <th>Minor</th>
                    <th>Reports</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for i, result in enumerate(results, 1):
        stats = result["statistics"]
        comparison_name = result.get("comparison") or f"Comparison {i}"
        
        html += f"""
                <tr>
                    <td><strong>{comparison_name}</strong></td>
                    <td>{stats['differences_found']}</td>
                    <td style="color: #e74c3c;"><strong>{stats['critical']}</strong></td>
                    <td style="color: #f39c12;"><strong>{stats['major']}</strong></td>
                    <td style="color: #3498db;"><strong>{stats['minor']}</strong></td>
                    <td>
                        <a href="{result['reports']['html']}" class="link">HTML</a> | 
                        <a href="{result['reports']['json']}" class="link">JSON</a>
                    </td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"\n✅ Summary generated: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Batch JSON Comparator")
        print("\nUsage:")
        print("  python3 batch_json_comparator.py consecutive [base_directory]")
        print("  python3 batch_json_comparator.py directories <old_dir> <new_dir>")
        print("\nExamples:")
        print("  python3 batch_json_comparator.py consecutive .")
        print("  python3 batch_json_comparator.py directories old_captures new_captures")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "consecutive":
        base_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        print("🔄 Batch comparing consecutive captures...")
        results = compare_consecutive_captures(base_dir)
        
        if results:
            generate_batch_summary(results, "batch_consecutive_summary.html")
            print(f"\n✨ Completed {len(results)} comparisons!")
    
    elif mode == "directories":
        if len(sys.argv) < 4:
            print("Error: directories mode requires <old_dir> and <new_dir>")
            sys.exit(1)
        
        old_dir = sys.argv[2]
        new_dir = sys.argv[3]
        
        print("📁 Batch comparing directories...")
        results = compare_directory_pair(old_dir, new_dir)
        
        if results:
            generate_batch_summary(results, "batch_directory_summary.html")
            print(f"\n✨ Completed {len(results)} comparisons!")
    
    else:
        print(f"Error: Unknown mode '{mode}'")
        sys.exit(1)

if __name__ == "__main__":
    main()
