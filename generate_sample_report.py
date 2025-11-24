#!/usr/bin/env python3
"""
Script to generate a sample enhanced HTML report using the sample verification summary data
"""

import json
import os

def generate_html_report(summary):
    """Generate an enhanced HTML report with better visualization of differences"""
    report_path = os.path.join(os.getcwd(), "enhanced_migration_verification_report.html")
    
    # Count differences
    total_sites = len(summary["sites_verified"])
    sites_with_differences = 0
    critical_issues = 0
    minor_differences = 0
    
    site_details = []
    for result in summary["comparison_results"]:
        has_critical = any(diff.get("severity") == "CRITICAL" for diff in result["differences"])
        has_minor = any(diff.get("severity") == "MINOR" for diff in result["differences"])
        has_any_diff = len(result["differences"]) > 0
        
        if has_any_diff:
            sites_with_differences += 1
            
        if has_critical:
            critical_issues += 1
        elif has_any_diff:  # Only count as minor if there are differences but no critical ones
            minor_differences += 1
            
        site_details.append({
            "name": result["site"],
            "has_critical": has_critical,
            "has_minor": has_minor and not has_critical,
            "differences": result["differences"]
        })
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Enhanced ACME Website Migration Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .critical {{ color: #d9534f; font-weight: bold; }}
        .minor {{ color: #f0ad4e; }}
        .identical {{ color: #5cb85c; }}
        .site-report {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
        .difference {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #5bc0de; }}
        .critical-diff {{ border-left-color: #d9534f; }}
        .minor-diff {{ border-left-color: #f0ad4e; }}
        pre {{ background-color: #f8f8f8; padding: 10px; overflow-x: auto; }}
        .warning {{ background-color: #fcf8e3; border-color: #faebcc; }}
    </style>
</head>
<body>
    <h1>ENHANCED ACME WEBSITE MIGRATION VERIFICATION REPORT</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Verification Timestamp:</strong> {summary["verification_timestamp"]}</p>
        <p><strong>Old Website:</strong> <a href="{summary["old_website_url"]}">{summary["old_website_url"]}</a></p>
        <p><strong>New Website:</strong> <a href="{summary["new_website_url"]}">{summary["new_website_url"]}</a></p>
        <p><strong>Total Sites Verified:</strong> {total_sites}</p>
        <p><strong>Sites with Differences:</strong> {sites_with_differences}</p>
        <p><strong>Sites Identical:</strong> {total_sites - sites_with_differences}</p>
        <p><strong>Critical Issues:</strong> <span class="critical">{critical_issues}</span></p>
        <p><strong>Minor Differences:</strong> <span class="minor">{minor_differences}</span></p>
    </div>
    
    <h2>Detailed Site Analysis</h2>"""
    
    for i, site_detail in enumerate(site_details, 1):
        site_name = site_detail["name"]
        has_critical = site_detail["has_critical"]
        has_minor = site_detail["has_minor"]
        differences = site_detail["differences"]
        
        # Determine status class
        if has_critical:
            status_text = '<span class="critical">Critical Differences Found</span>'
        elif has_minor:
            status_text = '<span class="minor">Minor Differences Found</span>'
        else:
            status_text = '<span class="identical">Identical</span>'
        
        html_content += f"""
    <div class="site-report">
        <h3>{i}. {site_name} {status_text}</h3>"""
        
        if differences:
            for diff in differences:
                diff_type = diff.get("type", "unknown")
                severity = diff.get("severity", "MINOR")
                details = diff.get("details", "")
                old_val = diff.get("old_value", "")
                new_val = diff.get("new_value", "")
                
                # Determine CSS class based on severity
                css_class = "critical-diff" if severity == "CRITICAL" else "minor-diff"
                severity_label = "CRITICAL" if severity == "CRITICAL" else "MINOR"
                
                html_content += f"""
        <div class="difference {css_class}">
            <h4>{severity_label}: {details}</h4>"""
                
                if old_val is not None or new_val is not None:
                    html_content += f"""
            <p><strong>Values:</strong> """
                    if old_val is not None:
                        html_content += f"Old: {old_val} "
                    if new_val is not None:
                        html_content += f"New: {new_val}"
                    html_content += "</p>"
                
                # Add impact assessment
                if severity == "CRITICAL":
                    html_content += """
            <p><strong>Impact:</strong> <span class="critical">CRITICAL - Data loss detected, requires immediate investigation</span></p>"""
                else:
                    html_content += """
            <p><strong>Impact:</strong> <span class="minor">Minor difference, may not affect functionality</span></p>"""
                
                html_content += """
        </div>"""
        else:
            html_content += """
        <p>No differences found between old and new websites.</p>"""
        
        html_content += """
    </div>"""
    
    html_content += f"""
    <h2>Recommendations</h2>
    <ol>"""
    
    # Add specific recommendations based on findings
    if critical_issues > 0:
        html_content += f"""
        <li><span class="critical">CRITICAL:</span> Investigate {critical_issues} critical issues immediately
            <br><strong>Action:</strong> Check data migration process for sites with critical data loss</li>"""
    
    if minor_differences > 0:
        html_content += f"""
        <li><span class="minor">MINOR:</span> Review {minor_differences} sites with minor differences
            <br><strong>Action:</strong> Verify that minor changes are intentional enhancements</li>"""
    
    html_content += f"""
        <li><strong>OVERALL:</strong> {total_sites - sites_with_differences} out of {total_sites} sites migrated successfully
            <br><strong>Action:</strong> Continue monitoring, focus on resolving critical issues first</li>
    </ol>
    
    <h2>Verification Methodology</h2>
    <ul>
        <li>Page source comparison for structural differences</li>
        <li>Visible text comparison for content differences</li>
        <li>Numeric value extraction and comparison for asset counts and metrics</li>
        <li>Automated verification across all sites in dropdown menu</li>
        <li>Detailed reporting of all discrepancies found</li>
    </ul>
    
    <p><em>This report was automatically generated by the Enhanced Migration Verification Framework.</em></p>
</body>
</html>"""
    
    # Write the HTML report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Enhanced HTML report generated: {report_path}")
    return report_path

def main():
    # Load the sample verification summary
    with open("sample_verification_summary.json", "r") as f:
        summary = json.load(f)
    
    # Generate the HTML report
    report_path = generate_html_report(summary)
    print(f"Sample report generated successfully at: {report_path}")

if __name__ == "__main__":
    main()