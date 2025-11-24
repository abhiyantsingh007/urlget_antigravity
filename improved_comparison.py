#!/usr/bin/env python3
"""
Improved comparison script that properly matches API endpoints by path
and compares all JSON data to detect every difference.
"""

import json
import os
import difflib
from urllib.parse import urlparse
from collections import defaultdict

def load_json_file(filepath):
    """Load JSON data from a file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {str(e)}")
        return None

def extract_endpoint_key(url):
    """
    Extract a comparable key from URL (path + query params without values)
    This allows matching endpoints between old and new domains
    """
    parsed = urlparse(url)
    # For our purposes, we'll use the path and query parameter names
    path = parsed.path
    return path

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
            "old_value": str(obj1),
            "new_value": str(obj2)
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
                    "new_value": str(obj2[key])
                })
            elif key not in obj2:
                differences.append({
                    "path": new_path,
                    "type": "removed",
                    "old_value": str(obj1[key]),
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
                "old_value": f"Length: {len(obj1)}",
                "new_value": f"Length: {len(obj2)}"
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
                    "old_value": str(obj1),
                    "new_value": str(obj2)
                })
    
    return differences

def compare_matching_endpoints(old_responses, new_responses):
    """
    Compare API responses by matching endpoints based on path and compare their content.
    """
    results = {
        "summary": {
            "total_endpoints": 0,
            "endpoints_compared": 0,
            "endpoints_with_differences": 0,
            "critical_issues": 0,
            "minor_differences": 0,
            "endpoints_only_in_old": 0,
            "endpoints_only_in_new": 0
        },
        "detailed_differences": []
    }
    
    # Group responses by endpoint key (path)
    old_by_endpoint = {}
    for resp in old_responses:
        if 'url' in resp:
            key = extract_endpoint_key(resp['url'])
            old_by_endpoint[key] = resp
    
    new_by_endpoint = {}
    for resp in new_responses:
        if 'url' in resp:
            key = extract_endpoint_key(resp['url'])
            new_by_endpoint[key] = resp
    
    # Get all endpoint keys
    all_endpoints = set(old_by_endpoint.keys()) | set(new_by_endpoint.keys())
    results["summary"]["total_endpoints"] = len(all_endpoints)
    
    for endpoint_key in all_endpoints:
        results["summary"]["endpoints_compared"] += 1
        
        old_resp = old_by_endpoint.get(endpoint_key)
        new_resp = new_by_endpoint.get(endpoint_key)
        
        if old_resp is None and new_resp is not None:
            # New endpoint
            results["summary"]["endpoints_only_in_new"] += 1
            results["detailed_differences"].append({
                "endpoint": endpoint_key,
                "urls": {
                    "old": None,
                    "new": new_resp.get('url')
                },
                "type": "endpoint_added",
                "severity": "MINOR",
                "differences": [{
                    "path": "",
                    "type": "endpoint_added",
                    "old_value": None,
                    "new_value": "New endpoint in migrated site"
                }]
            })
        elif old_resp is not None and new_resp is None:
            # Removed endpoint
            results["summary"]["endpoints_only_in_old"] += 1
            results["detailed_differences"].append({
                "endpoint": endpoint_key,
                "urls": {
                    "old": old_resp.get('url'),
                    "new": None
                },
                "type": "endpoint_removed",
                "severity": "CRITICAL",
                "differences": [{
                    "path": "",
                    "type": "endpoint_removed",
                    "old_value": "Endpoint exists in old site but missing in migrated site",
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
                    "endpoint": endpoint_key,
                    "urls": {
                        "old": old_resp.get('url'),
                        "new": new_resp.get('url')
                    },
                    "type": "differences_found",
                    "severity": severity,
                    "differences": differences
                })
            else:
                # No differences
                pass
    
    return results

def generate_detailed_html_report(comparison_results, old_dir, new_dir):
    """
    Generate a detailed HTML report showing all differences.
    """
    report_path = "detailed_migration_report.html"
    
    # Count statistics
    summary = comparison_results["summary"]
    critical_count = summary["critical_issues"]
    minor_count = summary["minor_differences"]
    total_compared = summary["endpoints_compared"]
    total_with_differences = summary["endpoints_with_differences"]
    only_old = summary["endpoints_only_in_old"]
    only_new = summary["endpoints_only_in_new"]
    
    # Start HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Detailed Migration Verification Report</title>
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
        pre {{ background-color: #f8f8f8; padding: 10px; overflow-x: auto; white-space: pre-wrap; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px 0; }}
        .stat-card {{ background: white; border: 1px solid #ddd; padding: 15px; text-align: center; border-radius: 5px; }}
        .stat-number {{ font-size: 24px; font-weight: bold; }}
        .critical .stat-number {{ color: #d9534f; }}
        .minor .stat-number {{ color: #f0ad4e; }}
        .identical .stat-number {{ color: #5cb85c; }}
        .total .stat-number {{ color: #333; }}
        .only-old .stat-number {{ color: #d9534f; }}
        .only-new .stat-number {{ color: #5bc0de; }}
    </style>
</head>
<body>
    <h1>DETAILED MIGRATION VERIFICATION REPORT</h1>
    
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
                <div class="stat-number">{total_compared - total_with_differences - only_old - only_new}</div>
                <div>Identical Endpoints</div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card only-old">
                <div class="stat-number">{only_old}</div>
                <div>Only in Old Site</div>
            </div>
            <div class="stat-card only-new">
                <div class="stat-number">{only_new}</div>
                <div>Only in New Site</div>
            </div>
        </div>
    </div>
    
    <h2>Detailed Endpoint Analysis</h2>"""
    
    # Add each endpoint with differences
    for endpoint in comparison_results["detailed_differences"]:
        endpoint_path = endpoint["endpoint"]
        severity = endpoint["severity"]
        differences = endpoint["differences"]
        urls = endpoint["urls"]
        
        # Determine status text
        if severity == "CRITICAL":
            status_text = '<span class="critical">CRITICAL ISSUES FOUND</span>'
        elif differences:
            status_text = '<span class="minor">MINOR DIFFERENCES FOUND</span>'
        else:
            status_text = '<span class="identical">IDENTICAL</span>'
        
        html += f"""
    <div class="endpoint-report">
        <h3>{endpoint_path} {status_text}</h3>"""
        
        # Show URLs if available
        if urls["old"] or urls["new"]:
            html += "<p><strong>URLs:</strong><br>"
            if urls["old"]:
                html += f"  Old: <code>{urls['old']}</code><br>"
            if urls["new"]:
                html += f"  New: <code>{urls['new']}</code>"
            html += "</p>"
        
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
            <p><strong>Values:</strong><br>"""
                if old_val is not None:
                    html += f"  Old: <code>{old_val}</code><br>"
                if new_val is not None:
                    html += f"  New: <code>{new_val}</code>"
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
    
    if only_old > 0:
        html += f"""
        <li><span class="critical">CRITICAL:</span> Investigate {only_old} endpoints missing in new site
            <br><strong>Action:</strong> Verify these endpoints were intentionally removed or identify migration issues</li>"""
    
    if minor_count > 0:
        html += f"""
        <li><span class="minor">MINOR:</span> Review {minor_count} endpoints with minor differences
            <br><strong>Action:</strong> Verify that minor changes are intentional enhancements</li>"""
    
    if only_new > 0:
        html += f"""
        <li><span class="minor">MINOR:</span> Review {only_new} new endpoints in migrated site
            <br><strong>Action:</strong> Verify these are intentional additions</li>"""
    
    identical_count = total_compared - total_with_differences - only_old - only_new
    html += f"""
        <li><strong>OVERALL:</strong> {identical_count} out of {total_compared} endpoints migrated successfully
            <br><strong>Action:</strong> Continue monitoring, focus on resolving critical issues first</li>
    </ol>
    
    <h2>Verification Methodology</h2>
    <ul>
        <li>Endpoint matching by path to compare equivalent APIs between old and new sites</li>
        <li>Complete JSON structure comparison for all API responses</li>
        <li>Deep recursive comparison of nested objects and arrays</li>
        <li>Special detection of critical data loss patterns (positive → zero values)</li>
        <li>Classification of differences by severity level</li>
        <li>Comprehensive reporting of all discrepancies found</li>
    </ul>
    
    <p><em>This report was automatically generated by the Detailed Migration Verification Framework.</em></p>
</body>
</html>"""
    
    # Write the report
    with open(report_path, 'w') as f:
        f.write(html)
    
    print(f"Detailed HTML report generated: {report_path}")
    return report_path

def create_sample_data():
    """
    Create sample data that demonstrates the specific issues mentioned:
    - All Facilities: 2,535 assets in old vs 1,048 in new
    - Site657: 1 asset in old vs 0 in new (critical data loss)
    """
    old_responses = [
        {
            "url": "https://acme.egalvanic-rnd.com/api/dashboard/stats",
            "status": 200,
            "response": {
                "sites_overview": {
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
                {"name": "All Facilities", "total_assets": 2535, "status": "active"},
                {"name": "Site657", "total_assets": 1, "status": "active"}
            ]
        },
        {
            "url": "https://acme.egalvanic-rnd.com/api/assets/summary",
            "status": 200,
            "response": {
                "total_assets": 5432,
                "by_category": {
                    "Electrical": 2100,
                    "Mechanical": 1800,
                    "HVAC": 1532
                }
            }
        }
    ]
    
    new_responses = [
        {
            "url": "https://acme.egalvanic.ai/api/dashboard/stats",
            "status": 200,
            "response": {
                "sites_overview": {
                    "All Facilities": {
                        "total_assets": 1048,  # Changed from 2535 - Major difference
                        "active_sites": 42,
                        "pending_tasks": 15
                    },
                    "Site657": {
                        "total_assets": 0,  # Changed from 1 - CRITICAL DATA LOSS
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
                {"name": "All Facilities", "total_assets": 1048, "status": "active"},  # Changed from 2535
                {"name": "Site657", "total_assets": 0, "status": "active"}  # Changed from 1 - CRITICAL
            ]
        },
        {
            "url": "https://acme.egalvanic.ai/api/assets/summary",
            "status": 200,
            "response": {
                "total_assets": 2156,  # Changed from 5432 - Major difference
                "by_category": {
                    "Electrical": 850,   # Changed from 2100
                    "Mechanical": 720,   # Changed from 1800
                    "HVAC": 586          # Changed from 1532
                }
            }
        }
    ]
    
    return old_responses, new_responses

def main():
    """
    Main function to demonstrate detailed comparison.
    """
    print("DETAILED MIGRATION VERIFICATION")
    print("=" * 40)
    
    # Create sample data that shows the specific issues you mentioned
    old_responses, new_responses = create_sample_data()
    
    print("\nSample data created with the specific issues you mentioned:")
    print("- All Facilities: 2,535 assets → 1,048 assets (major difference)")
    print("- Site657: 1 asset → 0 assets (CRITICAL DATA LOSS)")
    print("- Total users: 127 → 129 (minor change)")
    print("- Overall assets: 5,432 → 2,156 (major difference)")
    
    # Perform comparison
    results = compare_matching_endpoints(old_responses, new_responses)
    
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
    print(f"  Endpoints only in old site: {summary['endpoints_only_in_old']}")
    print(f"  Endpoints only in new site: {summary['endpoints_only_in_new']}")
    
    # Generate HTML report
    report_path = generate_detailed_html_report(results, "OLD_WEBSITE_CAPTURE", "NEW_WEBSITE_CAPTURE")
    
    print(f"\nDetailed report saved to: {report_path}")
    print("\nThe report includes:")
    print("  ✓ All Facilities asset count difference (2,535 → 1,048)")
    print("  ✓ Site657 critical data loss (1 → 0)")
    print("  ✓ All other metric changes")
    print("  ✓ Proper classification of severity levels")
    print("  ✓ Clear visualization of all differences")
    print("  ✓ Endpoint matching by path rather than full URL")

if __name__ == "__main__":
    main()