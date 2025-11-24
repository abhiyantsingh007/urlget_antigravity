#!/usr/bin/env python3
"""
Automated Migration Comparison
Compares captured data and generates HTML report showing all differences
"""
import json
import os
from datetime import datetime
from collections import defaultdict

def load_capture_data(filename):
    """Load captured data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def extract_site_data(api_responses):
    """Extract site-specific data from API responses"""
    site_data = defaultdict(lambda: {
        'total_assets': None,
        'issues': None,
        'tasks': None,
        'found_in_urls': []
    })
    
    for api_entry in api_responses:
        url = api_entry.get('url', '')
        response = api_entry.get('response', {})
        
        if not isinstance(response, dict):
            continue
        
        # STRUCTURE 1: site-overview endpoint contains dashboard data
        # /api/lookup/site-overview/{site_id} returns {name:..., data: {total_assets:...}}
        if 'site-overview' in url:
            site_name = response.get('name')
            if site_name and 'data' in response:
                data_section = response['data']
                if isinstance(data_section, dict):
                    if 'total_assets' in data_section:
                        site_data[site_name]['total_assets'] = data_section['total_assets']
                        site_data[site_name]['found_in_urls'].append(url)
                    if 'open_issues_count' in data_section:
                        site_data[site_name]['issues'] = data_section['open_issues_count']
                    if 'pending_tasks_count' in data_section:
                        site_data[site_name]['tasks'] = data_section['pending_tasks_count']
        
        # STRUCTURE 2: {sites: {Site657: {total_assets: 1}}}
        if 'sites' in response and isinstance(response['sites'], dict):
            for site_name, site_info in response['sites'].items():
                if isinstance(site_info, dict):
                    if 'total_assets' in site_info:
                        site_data[site_name]['total_assets'] = site_info['total_assets']
                        site_data[site_name]['found_in_urls'].append(url)
                    if 'issues' in site_info:
                        site_data[site_name]['issues'] = site_info['issues']
                    if 'tasks' in site_info or 'pending_tasks' in site_info:
                        site_data[site_name]['tasks'] = site_info.get('tasks') or site_info.get('pending_tasks')
        
        # STRUCTURE 3: {sites_overview: [{name: Site657, total_assets: 1}]}
        if 'sites_overview' in response:
            sites = response['sites_overview']
            if isinstance(sites, list):
                for site_info in sites:
                    if isinstance(site_info, dict) and 'name' in site_info:
                        site_name = site_info['name']
                        if 'total_assets' in site_info or 'assets' in site_info:
                            site_data[site_name]['total_assets'] = site_info.get('total_assets') or site_info.get('assets')
                            site_data[site_name]['found_in_urls'].append(url)
            elif isinstance(sites, dict):
                for site_name, site_info in sites.items():
                    if isinstance(site_info, dict) and 'total_assets' in site_info:
                        site_data[site_name]['total_assets'] = site_info['total_assets']
                        site_data[site_name]['found_in_urls'].append(url)
        
        # STRUCTURE 4: Direct list of sites
        if isinstance(response, list):
            for item in response:
                if isinstance(item, dict) and 'name' in item:
                    site_name = item['name']
                    if 'total_assets' in item or 'assets' in item:
                        site_data[site_name]['total_assets'] = item.get('total_assets') or item.get('assets')
                        site_data[site_name]['found_in_urls'].append(url)
    
    return dict(site_data)

def compare_site_data(old_sites, new_sites):
    """Compare site data and identify differences"""
    all_site_names = set(old_sites.keys()) | set(new_sites.keys())
    
    differences = []
    
    for site_name in all_site_names:
        old_data = old_sites.get(site_name, {})
        new_data = new_sites.get(site_name, {})
        
        old_assets = old_data.get('total_assets')
        new_assets = new_data.get('total_assets')
        
        if old_assets is not None and new_assets is not None:
            if old_assets != new_assets:
                # Determine severity
                if old_assets > 0 and new_assets == 0:
                    severity = 'CRITICAL'
                elif abs(old_assets - new_assets) > 100:
                    severity = 'MAJOR'
                else:
                    severity = 'MINOR'
                
                differences.append({
                    'site': site_name,
                    'field': 'Total Assets',
                    'old_value': old_assets,
                    'new_value': new_assets,
                    'change': new_assets - old_assets,
                    'severity': severity,
                    'old_urls': old_data.get('found_in_urls', []),
                    'new_urls': new_data.get('found_in_urls', [])
                })
        elif old_assets is not None and new_assets is None:
            differences.append({
                'site': site_name,
                'field': 'Total Assets',
                'old_value': old_assets,
                'new_value': 'MISSING',
                'change': None,
                'severity': 'CRITICAL',
                'old_urls': old_data.get('found_in_urls', []),
                'new_urls': []
            })
        elif old_assets is None and new_assets is not None:
            differences.append({
                'site': site_name,
                'field': 'Total Assets',
                'old_value': 'MISSING',
                'new_value': new_assets,
                'change': None,
                'severity': 'MINOR',
                'old_urls': [],
                'new_urls': new_data.get('found_in_urls', [])
            })
    
    return differences

def generate_html_report(old_capture, new_capture, differences):
    """Generate HTML report"""
    old_meta = old_capture['metadata']
    new_meta = new_capture['metadata']
    
    critical_count = sum(1 for d in differences if d['severity'] == 'CRITICAL')
    major_count = sum(1 for d in differences if d['severity'] == 'MAJOR')
    minor_count = sum(1 for d in differences if d['severity'] == 'MINOR')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Migration Verification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
        .summary-item {{ background: white; padding: 15px; border-radius: 5px; text-align: center; }}
        .summary-item h3 {{ margin: 0; font-size: 32px; }}
        .summary-item p {{ margin: 5px 0 0 0; color: #666; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .major {{ color: #f57c00; font-weight: bold; }}
        .minor {{ color: #fbc02d; }}
        .success {{ color: #388e3c; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; font-weight: bold; }}
        tr:hover {{ background: #f5f5f5; }}
        .badge {{ padding: 4px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }}
        .badge-critical {{ background: #d32f2f; color: white; }}
        .badge-major {{ background: #f57c00; color: white; }}
        .badge-minor {{ background: #fbc02d; color: black; }}
        .metadata {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 14px; }}
        .url-list {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .change-positive {{ color: #388e3c; }}
        .change-negative {{ color: #d32f2f; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Migration Verification Report</h1>
        
        <div class="metadata">
            <p><strong>Old Website:</strong> {old_meta['base_url']}</p>
            <p><strong>New Website:</strong> {new_meta['base_url']}</p>
            <p><strong>Old Capture Time:</strong> {old_meta['capture_time']}</p>
            <p><strong>New Capture Time:</strong> {new_meta['capture_time']}</p>
            <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>{old_meta['total_api_responses']}</h3>
                    <p>Old API Responses</p>
                </div>
                <div class="summary-item">
                    <h3>{new_meta['total_api_responses']}</h3>
                    <p>New API Responses</p>
                </div>
                <div class="summary-item">
                    <h3 class="critical">{critical_count}</h3>
                    <p>Critical Issues</p>
                </div>
                <div class="summary-item">
                    <h3 class="major">{major_count}</h3>
                    <p>Major Issues</p>
                </div>
                <div class="summary-item">
                    <h3 class="minor">{minor_count}</h3>
                    <p>Minor Issues</p>
                </div>
            </div>
        </div>
        
        <h2>Site Comparison Results</h2>
        
        {"<p class='success'>✅ No differences found! All sites match perfectly.</p>" if not differences else ""}
        
        {f'''<table>
            <thead>
                <tr>
                    <th>Site Name</th>
                    <th>Field</th>
                    <th>Old Value</th>
                    <th>New Value</th>
                    <th>Change</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
        ''' if differences else ''}
"""
    
    for diff in sorted(differences, key=lambda x: (0 if x['severity'] == 'CRITICAL' else 1 if x['severity'] == 'MAJOR' else 2, x['site'])):
        severity_class = diff['severity'].lower()
        badge_class = f"badge-{severity_class}"
        
        old_val = diff['old_value']
        new_val = diff['new_value']
        change = diff.get('change')
        
        change_display = ''
        if change is not None:
            change_class = 'change-positive' if change > 0 else 'change-negative'
            change_display = f'<span class="{change_class}">{change:+d}</span>'
        
        html += f"""
                <tr>
                    <td><strong>{diff['site']}</strong></td>
                    <td>{diff['field']}</td>
                    <td>{old_val}</td>
                    <td>{new_val}</td>
                    <td>{change_display}</td>
                    <td><span class="badge {badge_class}">{diff['severity']}</span></td>
                </tr>
        """
    
    if differences:
        html += """
            </tbody>
        </table>
        """
    
    html += """
        <h2>Recommendations</h2>
        <ul>
    """
    
    if critical_count > 0:
        html += f"""
            <li><span class="critical">CRITICAL:</span> {critical_count} critical issue(s) detected. 
            These indicate potential data loss (e.g., assets changing from positive to zero). 
            <strong>Immediate investigation required before migration.</strong></li>
        """
    
    if major_count > 0:
        html += f"""
            <li><span class="major">MAJOR:</span> {major_count} major difference(s) detected. 
            Review these changes to ensure they are intentional.</li>
        """
    
    if minor_count > 0:
        html += f"""
            <li><span class="minor">MINOR:</span> {minor_count} minor difference(s) detected. 
            These are small variations that likely don't affect functionality.</li>
        """
    
    if not differences:
        html += """
            <li class="success">All data migrated successfully with no discrepancies!</li>
        """
    
    html += """
        </ul>
        
        <div style="margin-top: 40px; padding: 20px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
            <h3 style="margin-top: 0;">📋 Next Steps</h3>
            <ol>
                <li>Review all CRITICAL issues immediately</li>
                <li>Verify MAJOR differences are intentional</li>
                <li>Document any acceptable differences</li>
                <li>Re-run this comparison after migration to verify fixes</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main(old_file, new_file):
    """Main comparison function"""
    print("\n" + "="*60)
    print("MIGRATION DATA COMPARISON")
    print("="*60 + "\n")
    
    # Load data
    print("1. Loading captured data...")
    old_capture = load_capture_data(old_file)
    new_capture = load_capture_data(new_file)
    print(f"   ✓ Old: {old_capture['metadata']['total_api_responses']} API responses")
    print(f"   ✓ New: {new_capture['metadata']['total_api_responses']} API responses\n")
    
    # Extract site data
    print("2. Extracting site data...")
    old_sites = extract_site_data(old_capture['api_responses'])
    new_sites = extract_site_data(new_capture['api_responses'])
    print(f"   ✓ Found {len(old_sites)} sites in old capture")
    print(f"   ✓ Found {len(new_sites)} sites in new capture\n")
    
    # Compare
    print("3. Comparing data...")
    differences = compare_site_data(old_sites, new_sites)
    
    critical = sum(1 for d in differences if d['severity'] == 'CRITICAL')
    major = sum(1 for d in differences if d['severity'] == 'MAJOR')
    minor = sum(1 for d in differences if d['severity'] == 'MINOR')
    
    print(f"   Found {len(differences)} difference(s):")
    print(f"   - CRITICAL: {critical}")
    print(f"   - MAJOR: {major}")
    print(f"   - MINOR: {minor}\n")
    
    if critical > 0:
        print("   ⚠️  CRITICAL ISSUES DETECTED:")
        for diff in differences:
            if diff['severity'] == 'CRITICAL':
                print(f"      - {diff['site']}: {diff['old_value']} → {diff['new_value']}")
        print()
    
    # Generate report
    print("4. Generating HTML report...")
    html = generate_html_report(old_capture, new_capture, differences)
    
    output_file = "migration_verification_report.html"
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"   ✓ Report saved to: {output_file}\n")
    print("="*60)
    print(f"✅ Comparison complete! Open {output_file} to view results.")
    print("="*60 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python automated_migration_comparison.py <old_capture.json> <new_capture.json>")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])
