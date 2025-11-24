#!/usr/bin/env python3
"""
SMART MIGRATION COMPARATOR
Intelligently compares API responses by filtering out noise and focusing on business data changes.

This improved approach:
1. Filters out expected changes (timestamps, tokens, session IDs, etc.)
2. Uses smart list comparison (by content, not position)
3. Focuses on business-critical data
4. Provides clearer, actionable reports
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

class SmartMigrationComparator:
    def __init__(self, old_capture_dir, new_capture_dir):
        self.old_capture_dir = old_capture_dir
        self.new_capture_dir = new_capture_dir
        
        # Fields that are expected to change - we'll ignore these
        self.ignore_fields = {
            'timestamp', 'created_at', 'updated_at', 'modified_at', 'date_created', 'date_modified',
            'access_token', 'id_token', 'refresh_token', 'token', 
            'session_id', 'session_key',
            'cache_key', 'etag', 'last_modified',
            'event_id',  # AWS Cognito event ID
            'iat', 'exp', 'auth_time',  # JWT claims
        }
        
        # Patterns for fields to ignore (regex)
        self.ignore_patterns = [
            r'.*_at$',  # Any field ending in _at (timestamps)
            r'.*_token$',  # Any token field
            r'.*_id$',  # Some IDs (but we'll be selective)
        ]
        
        # Fields that ARE important even if they look like IDs
        self.important_id_fields = {
            'sld_id', 'company_id', 'user_id', 'node_class_id', 'issue_class_id',
            'edge_class_id', 'entity_id'
        }
        
        # Business data fields that are critical
        self.critical_fields = {
            'total_assets', 'asset_count', 'count',
            'total', 'amount', 'value',
            'open_issues_count', 'pending_tasks_count', 'active_sessions_count',
            'name', 'label', 'display_name',
            'status', 'is_deleted', 'active'
        }
        
        self.results = {
            "summary": {
                "total_differences": 0,
                "critical_differences": 0,
                "major_differences": 0,
                "minor_differences": 0,
                "ignored_fields": 0
            },
            "endpoint_differences": [],
            "site_analysis": {}
        }
    
    def should_ignore_field(self, field_name):
        """Determine if a field should be ignored in comparison"""
        # Don't ignore if it's in the important list
        if field_name in self.important_id_fields:
            return False
        
        # Ignore if in the ignore list
        if field_name in self.ignore_fields:
            return True
        
        # Check patterns
        for pattern in self.ignore_patterns:
            if re.match(pattern, field_name):
                # But don't ignore if it's critical
                if field_name in self.critical_fields:
                    return False
                return True
        
        return False
    
    def is_critical_field(self, field_name):
        """Check if a field is business-critical"""
        return field_name in self.critical_fields
    
    def smart_list_compare(self, list1, list2, path=""):
        """
        Intelligently compare two lists.
        For lists of objects with IDs, match by ID first.
        Otherwise, try to match by content similarity.
        """
        differences = []
        
        # If lists are empty or same, no differences
        if list1 == list2:
            return differences
        
        # Check if lists contain dictionaries with 'id' field
        if (list1 and isinstance(list1[0], dict) and 'id' in list1[0] and
            list2 and isinstance(list2[0], dict) and 'id' in list2[0]):
            
            # Match by ID
            old_by_id = {item['id']: item for item in list1 if isinstance(item, dict)}
            new_by_id = {item['id']: item for item in list2 if isinstance(item, dict)}
            
            all_ids = set(old_by_id.keys()) | set(new_by_id.keys())
            
            for item_id in all_ids:
                item_path = f"{path}[id={item_id}]"
                
                if item_id not in old_by_id:
                    differences.append({
                        "path": item_path,
                        "type": "added",
                        "old_value": None,
                        "new_value": self._summarize_value(new_by_id[item_id]),
                        "severity": "MINOR"
                    })
                elif item_id not in new_by_id:
                    differences.append({
                        "path": item_path,
                        "type": "removed",
                        "old_value": self._summarize_value(old_by_id[item_id]),
                        "new_value": None,
                        "severity": "MAJOR"
                    })
                else:
                    # Compare the items
                    item_diffs = self.deep_compare(old_by_id[item_id], new_by_id[item_id], item_path)
                    differences.extend(item_diffs)
        
        # Check if lists contain dictionaries with 'name' field
        elif (list1 and isinstance(list1[0], dict) and 'name' in list1[0] and
              list2 and isinstance(list2[0], dict) and 'name' in list2[0]):
            
            # Match by name
            old_by_name = {item['name']: item for item in list1 if isinstance(item, dict)}
            new_by_name = {item['name']: item for item in list2 if isinstance(item, dict)}
            
            all_names = set(old_by_name.keys()) | set(new_by_name.keys())
            
            for name in all_names:
                item_path = f"{path}[name={name}]"
                
                if name not in old_by_name:
                    differences.append({
                        "path": item_path,
                        "type": "added",
                        "old_value": None,
                        "new_value": self._summarize_value(new_by_name[name]),
                        "severity": "MINOR"
                    })
                elif name not in new_by_name:
                    differences.append({
                        "path": item_path,
                        "type": "removed",
                        "old_value": self._summarize_value(old_by_name[name]),
                        "new_value": None,
                        "severity": "MAJOR"
                    })
                else:
                    # Compare the items
                    item_diffs = self.deep_compare(old_by_name[name], new_by_name[name], item_path)
                    differences.extend(item_diffs)
        
        else:
            # For other lists, check length first
            if len(list1) != len(list2):
                differences.append({
                    "path": path,
                    "type": "list_size_change",
                    "old_value": f"Length: {len(list1)}",
                    "new_value": f"Length: {len(list2)}",
                    "severity": "MAJOR"
                })
            
            # Compare element by element for common length
            min_len = min(len(list1), len(list2))
            for i in range(min_len):
                item_diffs = self.deep_compare(list1[i], list2[i], f"{path}[{i}]")
                differences.extend(item_diffs)
        
        return differences
    
    def _summarize_value(self, value, max_length=100):
        """Create a summary of a value for display"""
        if isinstance(value, (dict, list)):
            summary = json.dumps(value, separators=(',', ':'))[:max_length]
            if len(json.dumps(value, separators=(',', ':'))) > max_length:
                summary += "..."
            return summary
        return str(value)[:max_length]
    
    def deep_compare(self, obj1, obj2, path=""):
        """
        Recursively compare two objects with smart filtering.
        Ignores expected changes and focuses on business data.
        """
        differences = []
        
        # Skip if both are None or identical
        if obj1 == obj2:
            return differences
        
        # Type mismatch
        if type(obj1) != type(obj2):
            differences.append({
                "path": path,
                "type": "type_mismatch",
                "old_value": f"{type(obj1).__name__}: {self._summarize_value(obj1)}",
                "new_value": f"{type(obj2).__name__}: {self._summarize_value(obj2)}",
                "severity": "MAJOR"
            })
            return differences
        
        # Handle dictionaries
        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                
                # Check if we should ignore this field
                if self.should_ignore_field(key):
                    self.results["summary"]["ignored_fields"] += 1
                    continue
                
                if key not in obj1:
                    severity = "MAJOR" if self.is_critical_field(key) else "MINOR"
                    differences.append({
                        "path": new_path,
                        "type": "field_added",
                        "old_value": None,
                        "new_value": self._summarize_value(obj2[key]),
                        "severity": severity
                    })
                elif key not in obj2:
                    severity = "CRITICAL" if self.is_critical_field(key) else "MAJOR"
                    differences.append({
                        "path": new_path,
                        "type": "field_removed",
                        "old_value": self._summarize_value(obj1[key]),
                        "new_value": None,
                        "severity": severity
                    })
                else:
                    # Recursively compare
                    nested_diffs = self.deep_compare(obj1[key], obj2[key], new_path)
                    differences.extend(nested_diffs)
        
        # Handle lists
        elif isinstance(obj1, list):
            list_diffs = self.smart_list_compare(obj1, obj2, path)
            differences.extend(list_diffs)
        
        # Handle primitive values
        else:
            if obj1 != obj2:
                # Determine severity based on the field name and values
                severity = "MINOR"
                
                if isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
                    # Critical: data loss (positive to zero)
                    if obj1 > 0 and obj2 == 0:
                        severity = "CRITICAL"
                    # Major: large change
                    elif abs(obj2 - obj1) > 100 or (obj1 != 0 and abs((obj2 - obj1) / obj1) > 0.3):
                        severity = "MAJOR"
                
                # Check if field is critical
                field_name = path.split('.')[-1].split('[')[0]
                if self.is_critical_field(field_name):
                    severity = max(severity, "MAJOR")
                
                differences.append({
                    "path": path,
                    "type": "value_changed",
                    "old_value": obj1,
                    "new_value": obj2,
                    "severity": severity
                })
        
        return differences
    
    def load_capture(self, directory):
        """Load capture data from directory"""
        # Try different file names
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
                        data = json.load(f)
                        print(f"✅ Loaded: {filepath}")
                        return data
                except Exception as e:
                    print(f"❌ Error loading {filepath}: {e}")
        
        print(f"❌ No capture file found in {directory}")
        return None
    
    def extract_endpoint_path(self, url):
        """Extract comparable endpoint path from URL"""
        parsed = urlparse(url)
        return parsed.path
    
    def compare_captures(self):
        """Main comparison function"""
        print("\n" + "="*80)
        print("SMART MIGRATION COMPARISON")
        print("="*80)
        
        # Load captures
        old_data = self.load_capture(self.old_capture_dir)
        new_data = self.load_capture(self.new_capture_dir)
        
        if not old_data or not new_data:
            print("❌ Failed to load capture data")
            return
        
        # Get API responses
        old_responses = old_data.get('api_responses', [])
        new_responses = new_data.get('api_responses', [])
        
        print(f"\n📊 Old capture: {len(old_responses)} API responses")
        print(f"📊 New capture: {len(new_responses)} API responses")
        
        # Group by endpoint path
        old_by_path = {}
        new_by_path = {}
        
        for resp in old_responses:
            if isinstance(resp, dict) and 'url' in resp:
                path = self.extract_endpoint_path(resp['url'])
                old_by_path[path] = resp
        
        for resp in new_responses:
            if isinstance(resp, dict) and 'url' in resp:
                path = self.extract_endpoint_path(resp['url'])
                new_by_path[path] = resp
        
        # Compare endpoints
        all_paths = set(old_by_path.keys()) | set(new_by_path.keys())
        
        print(f"\n🔍 Comparing {len(all_paths)} unique endpoints...\n")
        
        for path in sorted(all_paths):
            old_resp = old_by_path.get(path)
            new_resp = new_by_path.get(path)
            
            if old_resp is None:
                print(f"  ➕ NEW: {path}")
                self.results["endpoint_differences"].append({
                    "endpoint": path,
                    "type": "endpoint_added",
                    "severity": "MINOR"
                })
            elif new_resp is None:
                print(f"  ➖ REMOVED: {path}")
                self.results["endpoint_differences"].append({
                    "endpoint": path,
                    "type": "endpoint_removed",
                    "severity": "CRITICAL"
                })
            else:
                # Compare response data only (skip metadata)
                old_response = old_resp.get('response', old_resp)
                new_response = new_resp.get('response', new_resp)
                
                differences = self.deep_compare(old_response, new_response, "response")
                
                if differences:
                    # Count severities
                    critical = sum(1 for d in differences if d['severity'] == 'CRITICAL')
                    major = sum(1 for d in differences if d['severity'] == 'MAJOR')
                    minor = sum(1 for d in differences if d['severity'] == 'MINOR')
                    
                    severity = "CRITICAL" if critical > 0 else "MAJOR" if major > 0 else "MINOR"
                    
                    status_icon = "🔴" if critical > 0 else "🟠" if major > 0 else "🟡"
                    
                    print(f"  {status_icon} CHANGED: {path}")
                    print(f"     └─ {critical} critical, {major} major, {minor} minor differences")
                    
                    self.results["endpoint_differences"].append({
                        "endpoint": path,
                        "type": "differences_found",
                        "severity": severity,
                        "old_url": old_resp.get('url', ''),
                        "new_url": new_resp.get('url', ''),
                        "differences": differences,
                        "counts": {
                            "critical": critical,
                            "major": major,
                            "minor": minor
                        }
                    })
                    
                    self.results["summary"]["total_differences"] += len(differences)
                    self.results["summary"]["critical_differences"] += critical
                    self.results["summary"]["major_differences"] += major
                    self.results["summary"]["minor_differences"] += minor
                else:
                    print(f"  ✅ IDENTICAL: {path}")
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().isoformat()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Smart Migration Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .critical {{ color: #dc3545; }}
        .major {{ color: #fd7e14; }}
        .minor {{ color: #ffc107; }}
        .success {{ color: #28a745; }}
        .endpoint {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ddd; }}
        .endpoint.critical {{ border-left-color: #dc3545; }}
        .endpoint.major {{ border-left-color: #fd7e14; }}
        .endpoint.minor {{ border-left-color: #ffc107; }}
        .difference {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 6px; }}
        .path {{ font-family: 'Courier New', monospace; color: #495057; font-size: 14px; }}
        .value {{ padding: 8px; background: #e9ecef; border-radius: 4px; margin: 5px 0; display: inline-block; max-width: 100%; word-break: break-all; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-left: 10px; }}
        .badge.critical {{ background: #fadbd8; color: #dc3545; }}
        .badge.major {{ background: #ffe5d0; color: #fd7e14; }}
        .badge.minor {{ background: #fff3cd; color: #ffc107; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Smart Migration Comparison Report</h1>
        <p>Intelligent comparison focusing on business-critical changes</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {timestamp}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number critical">{self.results['summary']['critical_differences']}</div>
                <div>Critical Issues</div>
            </div>
            <div class="stat">
                <div class="stat-number major">{self.results['summary']['major_differences']}</div>
                <div>Major Differences</div>
            </div>
            <div class="stat">
                <div class="stat-number minor">{self.results['summary']['minor_differences']}</div>
                <div>Minor Changes</div>
            </div>
            <div class="stat">
                <div class="stat-number success">{self.results['summary']['ignored_fields']}</div>
                <div>Ignored Noise</div>
            </div>
        </div>
        <p><strong>Old:</strong> {self.old_capture_dir}</p>
        <p><strong>New:</strong> {self.new_capture_dir}</p>
    </div>
"""
        
        # Group endpoints by severity
        critical_endpoints = [e for e in self.results["endpoint_differences"] if e.get("severity") == "CRITICAL"]
        major_endpoints = [e for e in self.results["endpoint_differences"] if e.get("severity") == "MAJOR"]
        minor_endpoints = [e for e in self.results["endpoint_differences"] if e.get("severity") == "MINOR"]
        
        # Critical endpoints
        if critical_endpoints:
            html += """
    <div class="summary">
        <h2>🔴 Critical Issues (Immediate Action Required)</h2>
"""
            for endpoint in critical_endpoints:
                html += self._render_endpoint(endpoint)
            html += "</div>"
        
        # Major endpoints
        if major_endpoints:
            html += """
    <div class="summary">
        <h2>🟠 Major Differences (Review Required)</h2>
"""
            for endpoint in major_endpoints:
                html += self._render_endpoint(endpoint)
            html += "</div>"
        
        # Minor endpoints
        if minor_endpoints:
            html += """
    <div class="summary">
        <h2>🟡 Minor Changes (Informational)</h2>
"""
            for endpoint in minor_endpoints:
                html += self._render_endpoint(endpoint)
            html += "</div>"
        
        html += """
</body>
</html>
"""
        
        # Save report
        report_path = os.path.join(os.getcwd(), "smart_migration_report.html")
        with open(report_path, 'w') as f:
            f.write(html)
        
        print(f"\n✅ Report saved to: {report_path}")
        
        # Also save JSON
        json_path = os.path.join(os.getcwd(), "smart_migration_report.json")
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✅ JSON data saved to: {json_path}")
    
    def _render_endpoint(self, endpoint):
        """Render an endpoint's differences as HTML"""
        severity_class = endpoint.get('severity', 'MINOR').lower()
        
        html = f"""
        <div class="endpoint {severity_class}">
            <h3><code>{endpoint['endpoint']}</code> <span class="badge {severity_class}">{endpoint['severity']}</span></h3>
"""
        
        if endpoint['type'] == 'endpoint_removed':
            html += "<p>❌ This endpoint was removed in the new version</p>"
        elif endpoint['type'] == 'endpoint_added':
            html += "<p>➕ This is a new endpoint in the new version</p>"
        elif 'differences' in endpoint:
            counts = endpoint.get('counts', {})
            html += f"<p>Found {counts.get('critical', 0)} critical, {counts.get('major', 0)} major, {counts.get('minor', 0)} minor differences</p>"
            
            # Show only critical and major differences by default
            for diff in endpoint['differences']:
                if diff['severity'] in ['CRITICAL', 'MAJOR']:
                    html += f"""
            <div class="difference">
                <strong>{diff['severity']}:</strong> {diff['type']} at <code class="path">{diff['path']}</code><br>
                Old: <span class="value">{self._format_value_html(diff['old_value'])}</span><br>
                New: <span class="value">{self._format_value_html(diff['new_value'])}</span>
            </div>
"""
        
        html += "</div>\n"
        return html
    
    def _format_value_html(self, value):
        """Format a value for HTML display"""
        if value is None:
            return "<em>None</em>"
        if isinstance(value, str) and len(value) > 100:
            return value[:100] + "..."
        return str(value)


def main():
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python smart_migration_comparator.py <old_capture_dir> <new_capture_dir>")
        print("\nExample:")
        print("  python smart_migration_comparator.py complete_captures_20251121_201827 complete_tab_captures_20251121_202444")
        sys.exit(1)
    
    old_dir = sys.argv[1]
    new_dir = sys.argv[2]
    
    if not os.path.exists(old_dir):
        print(f"❌ Old capture directory not found: {old_dir}")
        sys.exit(1)
    
    if not os.path.exists(new_dir):
        print(f"❌ New capture directory not found: {new_dir}")
        sys.exit(1)
    
    comparator = SmartMigrationComparator(old_dir, new_dir)
    comparator.compare_captures()


if __name__ == "__main__":
    main()
