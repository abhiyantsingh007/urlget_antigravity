#!/usr/bin/env python3
"""
SITE DATA COMPARATOR
Compares site-specific metrics (assets, issues, sessions) between old and new websites.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

class SiteDataComparator:
    def __init__(self, old_capture_dir, new_capture_dir):
        self.old_capture_dir = old_capture_dir
        self.new_capture_dir = new_capture_dir
        self.site_comparisons = []
        
    def load_capture(self, directory):
        """Load capture data from directory"""
        possible_files = [
            "complete_capture.json",
            "complete_tab_capture.json",
            "api_capture.json"
        ]
        
        for filename in possible_files:
            filepath = os.path.join(directory, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"❌ Error loading {filepath}: {e}")
        return None
    
    def extract_sites_data(self, capture_data):
        """Extract site-specific metrics from API responses"""
        sites = {}
        
        if not capture_data or 'api_responses' not in capture_data:
            return sites
        
        for response in capture_data['api_responses']:
            if not isinstance(response, dict) or 'response' not in response:
                continue
                
            resp_data = response['response']
            url = response.get('url', '')
            
            # Look for site overview data
            if isinstance(resp_data, dict):
                # Check for sites in the response
                if 'sites' in resp_data:
                    sites_data = resp_data['sites']
                    if isinstance(sites_data, dict):
                        for site_name, site_info in sites_data.items():
                            if site_name not in sites:
                                sites[site_name] = {}
                            
                            # Extract metrics
                            if isinstance(site_info, dict):
                                self._extract_metrics(sites[site_name], site_info)
                
                # Check for dashboard/overview endpoints
                if 'site-overview' in url or 'dashboard' in url:
                    # Extract site name from URL if possible
                    site_id = self._extract_site_id_from_url(url)
                    if site_id and 'data' in resp_data:
                        if site_id not in sites:
                            sites[site_id] = {}
                        self._extract_metrics(sites[site_id], resp_data.get('data', {}))
                
                # Check for slds (sites) endpoint
                if isinstance(resp_data, list):
                    for item in resp_data:
                        if isinstance(item, dict) and 'name' in item:
                            site_name = item['name']
                            if site_name not in sites:
                                sites[site_name] = {}
                            self._extract_metrics(sites[site_name], item)
        
        return sites
    
    def _extract_site_id_from_url(self, url):
        """Extract site ID from URL"""
        parts = url.split('/')
        for i, part in enumerate(parts):
            if part == 'site-overview' and i + 1 < len(parts):
                # Get the UUID after site-overview
                return parts[i + 1].split('?')[0]
        return None
    
    def _extract_metrics(self, site_dict, data):
        """Extract metrics from data and add to site_dict"""
        metric_mappings = {
            # Assets Tab
            'total_assets': ['total_assets', 'asset_count', 'assets_count'],
            
            # Issues Tab  
            'open_issues': ['open_issues', 'open_issues_count', 'unresolved_issues_count'],
            'unresolved_issues': ['unresolved_issues', 'open_issues'],
            'resolved_issues': ['resolved_issues', 'closed_issues'],
            'total_issues': ['total_issues', 'issues_count'],
            
            # Site Visits Tab
            'active_sessions': ['active_sessions', 'active_sessions_count', 'active_site_visits', 'sessions_count'],
            'completed_sessions': ['completed_sessions', 'completed_site_visits'],
            'total_sessions': ['total_sessions', 'total_site_visits'],
            
            # Tasks Tab
            'pending_tasks': ['pending_tasks', 'pending_tasks_count', 'tasks_count', 'open_tasks'],
            'completed_tasks': ['completed_tasks', 'closed_tasks'],
            'total_tasks': ['total_tasks'],
            
            # Opportunities Tab
            'opportunities_value': ['opportunities_value', 'opportunities_total_value'],
            'opportunities_count': ['opportunities_count', 'num_opportunities'],
            
            # Equipment Tab
            'equipment_at_risk': ['equipment_at_risk', 'total_asset_value', 'equipment_value'],
            
            # Reports/Analytics
            'compliance_score': ['compliance_score', 'compliance_percentage'],
            'safety_score': ['safety_score', 'safety_rating'],
        }
        
        for metric_name, possible_keys in metric_mappings.items():
            for key in possible_keys:
                if key in data and isinstance(data[key], (int, float)):
                    site_dict[metric_name] = data[key]
                    break
        
        # Also check for asset breakdown
        if 'asset_breakdown' in data and isinstance(data['asset_breakdown'], list):
            total = sum(item.get('count', 0) for item in data['asset_breakdown'] if isinstance(item, dict))
            if total > 0:
                site_dict['total_assets'] = total
    
    def compare_sites(self):
        """Compare site data between old and new captures"""
        print("\n" + "="*80)
        print("SITE DATA COMPARISON")
        print("="*80)
        
        # Load captures
        old_data = self.load_capture(self.old_capture_dir)
        new_data = self.load_capture(self.new_capture_dir)
        
        if not old_data or not new_data:
            print("❌ Failed to load capture data")
            return
        
        # Extract site data
        old_sites = self.extract_sites_data(old_data)
        new_sites = self.extract_sites_data(new_data)
        
        print(f"\n📊 Old capture: {len(old_sites)} sites found")
        print(f"📊 New capture: {len(new_sites)} sites found")
        
        # Get all unique sites
        all_sites = set(old_sites.keys()) | set(new_sites.keys())
        
        print(f"\n🔍 Comparing {len(all_sites)} unique sites...\n")
        
        # Compare each site
        for site_name in sorted(all_sites):
            old_site = old_sites.get(site_name, {})
            new_site = new_sites.get(site_name, {})
            
            # Get all metrics
            all_metrics = set(old_site.keys()) | set(new_site.keys())
            
            site_has_differences = False
            site_differences = []
            
            for metric in all_metrics:
                old_value = old_site.get(metric, 0)
                new_value = new_site.get(metric, 0)
                
                if old_value != new_value:
                    site_has_differences = True
                    change = new_value - old_value
                    severity = self._determine_severity(metric, old_value, new_value, change)
                    
                    site_differences.append({
                        'site': site_name,
                        'field': metric,
                        'old_value': old_value,
                        'new_value': new_value,
                        'change': change,
                        'severity': severity
                    })
            
            if site_has_differences:
                self.site_comparisons.extend(site_differences)
                
                # Print summary for this site
                critical = sum(1 for d in site_differences if d['severity'] == 'CRITICAL')
                major = sum(1 for d in site_differences if d['severity'] == 'MAJOR')
                minor = sum(1 for d in site_differences if d['severity'] == 'MINOR')
                
                icon = "🔴" if critical > 0 else "🟠" if major > 0 else "🟡"
                print(f"  {icon} {site_name}: {critical} critical, {major} major, {minor} minor differences")
            else:
                print(f"  ✅ {site_name}: No differences")
        
        # Generate report
        self.generate_report()
    
    def _determine_severity(self, metric, old_value, new_value, change):
        """Determine severity of change"""
        # Critical: data loss (positive to zero)
        if old_value > 0 and new_value == 0:
            return "CRITICAL"
        
        # For assets and issues, use stricter thresholds
        if metric in ['total_assets', 'open_issues']:
            abs_change = abs(change)
            
            # Critical: any decrease in assets
            if metric == 'total_assets' and change < 0:
                if abs_change > 100:
                    return "MAJOR"
                elif abs_change > 0:
                    return "MINOR"
            
            # Major: large change
            if abs_change > 100:
                return "MAJOR"
            elif abs_change > 10:
                return "MINOR"
        
        # For other metrics
        abs_change = abs(change)
        if abs_change > 1000:
            return "MAJOR"
        elif abs_change > 10:
            return "MINOR"
        
        return "MINOR"
    
    def generate_report(self):
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().isoformat()
        
        # Sort by severity
        severity_order = {'CRITICAL': 0, 'MAJOR': 1, 'MINOR': 2}
        sorted_comparisons = sorted(
            self.site_comparisons,
            key=lambda x: (severity_order.get(x['severity'], 3), x['site'])
        )
        
        # Count by severity
        critical_count = sum(1 for c in self.site_comparisons if c['severity'] == 'CRITICAL')
        major_count = sum(1 for c in self.site_comparisons if c['severity'] == 'MAJOR')
        minor_count = sum(1 for c in self.site_comparisons if c['severity'] == 'MINOR')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Site Data Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .critical {{ color: #dc3545; }}
        .major {{ color: #fd7e14; }}
        .minor {{ color: #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
        .badge-critical {{ background: #fadbd8; color: #dc3545; }}
        .badge-major {{ background: #ffe5d0; color: #fd7e14; }}
        .badge-minor {{ background: #fff3cd; color: #ffc107; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 Site Data Comparison Report</h1>
        <p>Site-by-site metric comparison between old and new environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number critical">{critical_count}</div>
                <div>Critical Issues</div>
            </div>
            <div class="stat">
                <div class="stat-number major">{major_count}</div>
                <div>Major Differences</div>
            </div>
            <div class="stat">
                <div class="stat-number minor">{minor_count}</div>
                <div>Minor Changes</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(self.site_comparisons)}</div>
                <div>Total Differences</div>
            </div>
        </div>
        <p><strong>Old:</strong> {self.old_capture_dir}</p>
        <p><strong>New:</strong> {self.new_capture_dir}</p>
    </div>
    
    <div class="summary">
        <h2>📋 Site Comparison Results</h2>
        <table>
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
"""
        
        for comp in sorted_comparisons:
            change_class = 'positive' if comp['change'] > 0 else 'negative'
            change_symbol = '+' if comp['change'] > 0 else ''
            severity_class = comp['severity'].lower()
            
            html += f"""
                <tr>
                    <td><strong>{comp['site']}</strong></td>
                    <td><code>{comp['field']}</code></td>
                    <td>{comp['old_value']:,}</td>
                    <td>{comp['new_value']:,}</td>
                    <td class="{change_class}">{change_symbol}{comp['change']:,}</td>
                    <td><span class="badge badge-{severity_class}">{comp['severity']}</span></td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        # Save report
        report_path = os.path.join(os.getcwd(), "site_comparison_report.html")
        with open(report_path, 'w') as f:
            f.write(html)
        
        print(f"\n✅ Report saved to: {report_path}")
        
        # Also save JSON
        json_path = os.path.join(os.getcwd(), "site_comparison_report.json")
        with open(json_path, 'w') as f:
            json.dump({
                'summary': {
                    'critical': critical_count,
                    'major': major_count,
                    'minor': minor_count,
                    'total': len(self.site_comparisons)
                },
                'comparisons': sorted_comparisons
            }, f, indent=2)
        print(f"✅ JSON data saved to: {json_path}")

def main():
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python3 site_data_comparator.py <old_capture_dir> <new_capture_dir>")
        sys.exit(1)
    
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    
    comparator = SiteDataComparator(old_dir, new_dir)
    comparator.compare_sites()

if __name__ == "__main__":
    main()
