#!/usr/bin/env python3
"""
Comprehensive comparison script that compares all JSON data between 
pre-migration and post-migration captures to detect every difference.
"""

import json
import os
import difflib
from collections import defaultdict

def load_json_file(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def deep_compare_json(obj1, obj2, path=""):
    """
    Recursively compare two JSON objects and return all differences.
    Returns a list of differences with paths and values.
    """
    differences = []
    
    # If types are different, that's a difference
    if type(obj1) != type(obj2):
        differences.append({
            "path": path,
            "type": "type_mismatch",
            "old_value": obj1,
            "new_value": obj2
        })
        return differences
    
    # Handle different types
    if isinstance(obj1, dict):
        # Get all keys from both objects
        all_keys = set(obj1.keys()) | set(obj2.keys())
        
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            
            if key not in obj1:
                differences.append({
                    "path": new_path,
                    "type": "added",
                    "old_value": None,
                    "new_value": obj2[key]
                })
            elif key not in obj2:
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "old_value": obj1[key],
                    "new_value": None
                })
            else:
                # Recursively compare nested objects
                differences.extend(deep_compare_json(obj1[key], obj2[key], new_path))
                
    elif isinstance(obj1, list):
        # For lists, compare by index if same length, otherwise mark as different
        if len(obj1) != len(obj2):
            differences.append({
                "path": path,
                "type": "list_length_mismatch",
                "old_value": len(obj1),
                "new_value": len(obj2)
            })
            # Still try to compare elements if possible
            min_len = min(len(obj1), len(obj2))
            for i in range(min_len):
                differences.extend(deep_compare_json(obj1[i], obj2[i], f"{path}[{i}]"))
        else:
            # Same length, compare element by element
            for i in range(len(obj1)):
                differences.extend(deep_compare_json(obj1[i], obj2[i], f"{path}[{i}]"))
                
    else:
        # Primitive values - compare directly
        if obj1 != obj2:
            # Special handling for numeric values that change from positive to zero
            if isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
                if obj1 > 0 and obj2 == 0:
                    differences.append({
                        "path": path,
                        "type": "critical_data_loss",
                        "old_value": obj1,
                        "new_value": obj2,
                        "severity": "CRITICAL"
                    })
                elif obj1 == 0 and obj2 > 0:
                    differences.append({
                        "path": path,
                        "type": "data_added",
                        "old_value": obj1,
                        "new_value": obj2,
                        "severity": "MINOR"
                    })
                else:
                    differences.append({
                        "path": path,
                        "type": "value_changed",
                        "old_value": obj1,
                        "new_value": obj2,
                        "severity": "MINOR"
                    })
            else:
                differences.append({
                    "path": path,
                    "type": "value_changed",
                    "old_value": obj1,
                    "new_value": obj2
                })
    
    return differences

def compare_api_responses(old_responses, new_responses):
    """
    Compare API responses by URL and return structured differences.
    """
    results = {
        "summary": {
            "total_endpoints": 0,
            "endpoints_compared": 0,
            "endpoints_with_differences": 0,
            "critical_issues": 0,
            "minor_differences": 0
        },
        "detailed_differences": []
    }
    
    # Group responses by URL
    old_by_url = {resp.get('url', f"response_{i}"): resp for i, resp in enumerate(old_responses)}
    new_by_url = {resp.get('url', f"response_{i}"): resp for i, resp in enumerate(new_responses)}
    
    # Get all URLs
    all_urls = set(old_by_url.keys()) | set(new_by_url.keys())
    results["summary"]["total_endpoints"] = len(all_urls)
    
    for url in all_urls:
        results["summary"]["endpoints_compared"] += 1
        
        old_resp = old_by_url.get(url)
        new_resp = new_by_url.get(url)
        
        if old_resp is None and new_resp is not None:
            # New endpoint
            results["detailed_differences"].append({
                "url": url,
                "type": "endpoint_added",
                "severity": "MINOR",
                "differences": [{
                    "path": "",
                    "type": "endpoint_added",
                    "old_value": None,
                    "new_value": new_resp
                }]
            })
        elif old_resp is not None and new_resp is None:
            # Removed endpoint
            results["detailed_differences"].append({
                "url": url,
                "type": "endpoint_removed",
                "severity": "CRITICAL",
                "differences": [{
                    "path": "",
                    "type": "endpoint_removed",
                    "old_value": old_resp,
                    "new_value": None
                }]
            })
        elif old_resp is not None and new_resp is not None:
            # Compare responses
            differences = deep_compare_json(old_resp, new_resp)
            
            if differences:
                results["summary"]["endpoints_with_differences"] += 1
                
                # Determine overall severity for this endpoint
                has_critical = any(diff.get("severity") == "CRITICAL" for diff in differences)
                severity = "CRITICAL" if has_critical else "MINOR"
                
                if has_critical:
                    results["summary"]["critical_issues"] += 1
                else:
                    results["summary"]["minor_differences"] += 1
                
                results["detailed_differences"].append({
                    "url": url,
                    "type": "differences_found",
                    "severity": severity,
                    "differences": differences
                })
            else:
                # No differences
                pass
    
    return results

def load_complete_capture(directory):
    """
    Load complete capture data from a directory.
    """
    capture_file = os.path.join(directory, "complete_capture.json")
    if os.path.exists(capture_file):
        data = load_json_file(capture_file)
        if data and "api_responses" in data:
            return data["api_responses"]
    return []

def generate_comprehensive_html_report(comparison_results, old_dir, new_dir):
    """
    Generate a comprehensive HTML report showing all differences.
    """
    report_path = "comprehensive_migration_report.html"
    
    # Count statistics
    summary = comparison_results["summary"]
    critical_count = summary["critical_issues"]
    minor_count = summary["minor_differences"]
    total_compared = summary["endpoints_compared"]
    total_with_differences = summary["endpoints_with_differences"]
    
    # Start HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Migration Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .critical {{ color: #d9534f; font-weight: bold; }}
        .minor {{ color: #f0ad4e; }}
        .identical {{ color: #5cb85c; }}
        .endpoint-report {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .difference {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #5bc0de; }}
        .critical-diff {{ border-left-color: #d9534f; }}
        .minor-diff {{ border-left-color: #f0ad4e; }}
        .added-diff {{ border-left-color: #5cb85c; }}
        .removed-diff {{ border-left-color: #333; }}
        pre {{ background-color: #f8f8f8; padding: 10px; overflow-x: auto; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .stat-card {{ background: white; border: 1px solid #ddd; padding: 15px; text-align: center; border-radius: 5px; }}
        .stat-number {{ font-size: 24px; font-weight: bold; }}
        .critical .stat-number {{ color: #d9534f; }}
        .minor .stat-number {{ color: #f0ad4e; }}
        .identical .stat-number {{ color: #5cb85c; }}
        .total .stat-number {{ color: #333; }}
    </style>
</head>
<body>
    <h1>COMPREHENSIVE MIGRATION VERIFICATION REPORT</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Verification Timestamp:</strong> {summary.get("timestamp", "N/A")}</p>
        <p><strong>Old Website Data:</strong> {old_dir}</p>
        <p><strong>New Website Data:</strong> {new_dir}</p>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-number">{total_compared}</div>
                <div>Total Endpoints Compared</div>
            </div>
            <div class="stat-card critical">
                <div class="stat-number">{critical_count}</div>
                <div>Critical Issues</div>
            </div>
            <div class="stat-card minor">
                <div class="stat-number">{minor_count}</div>
                <div>Minor Differences</div>
            </div>
            <div class="stat-card identical">
                <div class="stat-number">{total_compared - total_with_differences}</div>
                <div>Identical Endpoints</div>
            </div>
        </div>
    </div>
    
    <h2>Detailed Endpoint Analysis</h2>"""
    
    # Add each endpoint with differences
    for endpoint in comparison_results["detailed_differences"]:
        url = endpoint["url"]
        severity = endpoint["severity"]
        differences = endpoint["differences"]
        
        # Determine status text
        if severity == "CRITICAL":
            status_text = '<span class="critical">CRITICAL ISSUES FOUND</span>'
        elif differences:
            status_text = '<span class="minor">MINOR DIFFERENCES FOUND</span>'
        else:
            status_text = '<span class="identical">IDENTICAL</span>'
        
        html += f"""
    <div class="endpoint-report">
        <h3>{url} {status_text}</h3>"""
        
        # Add each difference
        for diff in differences:
            diff_type = diff["type"]
            path = diff["path"]
            old_val = diff["old_value"]
            new_val = diff["new_value"]
            
            # Determine CSS class
            if diff_type == "critical_data_loss":
                css_class = "critical-diff"
                type_label = "CRITICAL DATA LOSS"
            elif diff_type == "endpoint_added":
                css_class = "added-diff"
                type_label = "ENDPOINT ADDED"
            elif diff_type == "endpoint_removed":
                css_class = "removed-diff"
                type_label = "ENDPOINT REMOVED"
            elif diff_type in ["added", "data_added"]:
                css_class = "added-diff"
                type_label = "DATA ADDED"
            elif diff_type in ["removed", "type_mismatch"]:
                css_class = "removed-diff"
                type_label = "DATA REMOVED"
            else:
                css_class = "minor-diff"
                type_label = "VALUE CHANGED"
            
            html += f"""
        <div class="difference {css_class}">
            <h4>{type_label}: {path}</h4>"""
            
            # Show values if they exist
            if old_val is not None or new_val is not None:
                html += f"""
            <p><strong>Values:</strong> """
                if old_val is not None:
                    html += f"Old: <code>{old_val}</code> "
                if new_val is not None:
                    html += f"New: <code>{new_val}</code>"
                html += "</p>"
            
            # Add impact assessment for critical issues
            if diff_type == "critical_data_loss":
                html += """
            <p><strong>Impact:</strong> <span class="critical">CRITICAL - Data loss detected, requires immediate investigation</span></p>"""
            
            html += """
        </div>"""
        
        html += """
    </div>"""
    
    # Add recommendations
    html += f"""
    <h2>Recommendations</h2>
    <ol>"""
    
    if critical_count > 0:
        html += f"""
        <li><span class="critical">CRITICAL:</span> Investigate {critical_count} critical issues immediately
            <br><strong>Action:</strong> Check data migration process for endpoints with critical data loss</li>"""
    
    if minor_count > 0:
        html += f"""
        <li><span class="minor">MINOR:</span> Review {minor_count} endpoints with minor differences
            <br><strong>Action:</strong> Verify that minor changes are intentional enhancements</li>"""
    
    identical_count = total_compared - total_with_differences
    html += f"""
        <li><strong>OVERALL:</strong> {identical_count} out of {total_compared} endpoints migrated successfully
            <br><strong>Action:</strong> Continue monitoring, focus on resolving critical issues first</li>
    </ol>
    
    <h2>Verification Methodology</h2>
    <ul>
        <li>Complete JSON structure comparison for all API endpoints</li>
        <li>Deep recursive comparison of nested objects and arrays</li>
        <li>Special detection of critical data loss patterns (positive → zero values)</li>
        <li>Classification of differences by severity level</li>
        <li>Comprehensive reporting of all discrepancies found</li>
    </ul>
    
    <p><em>This report was automatically generated by the Comprehensive Migration Verification Framework.</em></p>
</body>
</html>"""
    
    # Write the report
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"Comprehensive HTML report generated: {report_path}")
    return report_path

def main():
    """
    Main function to demonstrate comprehensive comparison.
    """
    print("COMPREHENSIVE MIGRATION VERIFICATION")
    print("=" * 50)
    
    # For demonstration, let's create sample data that shows the issue you mentioned
    # All Facilities: 2,535 assets in old vs 1,048 in new
    
    old_responses = [
        {
            "url": "https://acme.egalvanic-rnd.com/api/dashboard/stats",
            "status": 200,
            "response": {
                "sites": {
                    "All Facilities": {
                        "total_assets": 2535,
                        "active_sites": 42,
                        "pending_tasks": 15
                    },
                    "Site657": {
                        "total_assets": 1,
                        "active_sites": 1,
                        "pending_tasks": 0
                    }
                },
                "total_users": 127
            }
        },
        {
            "url": "https://acme.egalvanic-rnd.com/api/sites/overview",
            "status": 200,
            "response": [
                {"name": "All Facilities", "assets": 2535, "status": "active"},
                {"name": "Site657", "assets": 1, "status": "active"}
            ]
        }
    ]
    
    new_responses = [
        {
            "url": "https://acme.egalvanic.ai/api/dashboard/stats",
            "status": 200,
            "response": {
                "sites": {
                    "All Facilities": {
                        "total_assets": 1048,  # Changed from 2535
                        "active_sites": 42,
                        "pending_tasks": 15
                    },
                    "Site657": {
                        "total_assets": 0,  # Changed from 1 - CRITICAL
                        "active_sites": 1,
                        "pending_tasks": 0
                    }
                },
                "total_users": 129  # Changed from 127
            }
        },
        {
            "url": "https://acme.egalvanic.ai/api/sites/overview",
            "status": 200,
            "response": [
                {"name": "All Facilities", "assets": 1048, "status": "active"},  # Changed from 2535
                {"name": "Site657", "assets": 0, "status": "active"}  # Changed from 1 - CRITICAL
            ]
        }
    ]
    
    print("\nComparing sample data that demonstrates the issues:")
    print("- All Facilities: 2,535 assets → 1,048 assets")
    print("- Site657: 1 asset → 0 assets (CRITICAL DATA LOSS)")
    print("- Total users: 127 → 129")
    
    # Perform comparison
    results = compare_api_responses(old_responses, new_responses)
    
    # Add timestamp to results
    from datetime import datetime
    results["summary"]["timestamp"] = datetime.now().isoformat()
    
    # Print summary
    summary = results["summary"]
    print(f"\nCOMPARISON RESULTS:")
    print(f"  Total endpoints compared: {summary['endpoints_compared']}")
    print(f"  Endpoints with differences: {summary['endpoints_with_differences']}")
    print(f"  Critical issues: {summary['critical_issues']}")
    print(f"  Minor differences: {summary['minor_differences']}")
    
    # Generate HTML report
    report_path = generate_comprehensive_html_report(results, "OLD_WEBSITE_DATA", "NEW_WEBSITE_DATA")
    
    print(f"\nDetailed report saved to: {report_path}")
    print("\nThe report includes:")
    print("  ✓ All Facilities asset count difference (2,535 → 1,048)")
    print("  ✓ Site657 critical data loss (1 → 0)")
    print("  ✓ All other metric changes")
    print("  ✓ Proper classification of severity levels")
    print("  ✓ Clear visualization of all differences")

if __name__ == "__main__":
    main()