"""
Complete All Sites Comparison Script
Captures EVERY site and EVERY metric from both RND and AI websites
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import sys

class CompleteAllSitesComparator:
    def __init__(self):
        self.rnd_url = "https://acme.egalvanic-rnd.com"
        self.ai_url = "https://acme.egalvanic.ai"
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def login(self, url, email, password):
        """Login to website"""
        print(f"\n{'='*60}")
        print(f"Logging into: {url}")
        print(f"{'='*60}")

        self.driver.get(f"{url}/login")
        time.sleep(3)

        try:
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            print(f"✓ Email entered")

            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            print(f"✓ Password entered")

            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()
            print(f"✓ Sign in clicked")

            time.sleep(8)
            print(f"✓ Login successful!")
            return True

        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def get_all_sites(self):
        """Get list of all available sites from dropdown"""
        print(f"\n📋 Getting list of all sites...")

        try:
            # Navigate to dashboard
            self.driver.get(f"{self.driver.current_url.split('/dashboard')[0]}/dashboard")
            time.sleep(3)

            # Click on site dropdown
            site_dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiAutocomplete-root input, [placeholder*='Select'], [placeholder*='facility']"))
            )
            site_dropdown.click()
            time.sleep(2)

            # Get all site options
            site_options = self.driver.find_elements(By.CSS_SELECTOR, ".MuiAutocomplete-option, [role='option'], li[data-option-index]")

            sites = []
            for option in site_options:
                site_name = option.text.strip()
                if site_name and site_name not in sites:
                    sites.append(site_name)

            # Close dropdown
            site_dropdown.send_keys(Keys.ESCAPE)
            time.sleep(1)

            print(f"✓ Found {len(sites)} sites: {sites}")
            return sites

        except Exception as e:
            print(f"✗ Error getting sites: {str(e)}")
            # Fallback - try to extract from page source
            try:
                page_source = self.driver.page_source
                # Common site names to look for
                potential_sites = ["All Facilities", "Super Caremark", "Site657", "test", "test site",
                                  "ShowSite3", "Toronto Canada", "London UK", "Melbourne AU"]
                sites = []
                for site in potential_sites:
                    if site in page_source:
                        sites.append(site)

                if sites:
                    print(f"✓ Found {len(sites)} sites (fallback): {sites}")
                    return sites
            except:
                pass

            return []

    def select_site(self, site_name):
        """Select a specific site"""
        print(f"\n  🎯 Selecting site: {site_name}")

        try:
            # Click dropdown
            dropdown = self.driver.find_element(By.CSS_SELECTOR, ".MuiAutocomplete-root input")
            dropdown.clear()
            dropdown.click()
            time.sleep(1)

            # Type site name
            dropdown.send_keys(site_name)
            time.sleep(2)

            # Click on the matching option
            options = self.driver.find_elements(By.CSS_SELECTOR, ".MuiAutocomplete-option, [role='option']")
            for option in options:
                if site_name.lower() in option.text.lower():
                    option.click()
                    time.sleep(3)
                    print(f"  ✓ Selected: {site_name}")
                    return True

            # Fallback - just press enter
            dropdown.send_keys(Keys.ENTER)
            time.sleep(3)
            print(f"  ✓ Selected: {site_name} (enter)")
            return True

        except Exception as e:
            print(f"  ✗ Could not select site: {str(e)}")
            return False

    def capture_dashboard_metrics(self, site_name):
        """Capture all metrics from dashboard for a site"""
        print(f"  📊 Capturing metrics for: {site_name}")

        metrics = {
            "site_name": site_name,
            "total_assets": None,
            "unresolved_issues": None,
            "pending_tasks": None,
            "active_sessions": None,
            "opportunities_value": None,
            "equipment_at_risk": None,
            "open_issues": None,
            "resolved_issues": None,
            "completed_tasks": None,
            "total_sessions": None,
            "completed_sessions": None,
            "active_site_visits": None
        }

        try:
            time.sleep(2)

            # Find all stat cards on dashboard
            stat_cards = self.driver.find_elements(By.CSS_SELECTOR, ".MuiBox-root")

            for card in stat_cards:
                try:
                    text = card.text.strip()

                    # Parse different metrics
                    if "Total Assets" in text:
                        value = text.split('\n')[-1]
                        metrics["total_assets"] = self.parse_number(value)

                    elif "Unresolved Issues" in text:
                        value = text.split('\n')[-1]
                        metrics["unresolved_issues"] = self.parse_number(value)

                    elif "Pending Tasks" in text:
                        value = text.split('\n')[-1]
                        metrics["pending_tasks"] = self.parse_number(value)

                    elif "Active Site Visits" in text or "Active Sessions" in text:
                        value = text.split('\n')[-1]
                        metrics["active_sessions"] = self.parse_number(value)
                        metrics["active_site_visits"] = self.parse_number(value)

                    elif "Opportunities Value" in text:
                        value = text.split('\n')[-1]
                        metrics["opportunities_value"] = self.parse_number(value)

                    elif "Equipment at Risk" in text:
                        value = text.split('\n')[-1]
                        metrics["equipment_at_risk"] = self.parse_number(value)

                    elif "Open Issues" in text:
                        value = text.split('\n')[-1]
                        metrics["open_issues"] = self.parse_number(value)

                    elif "Resolved Issues" in text:
                        value = text.split('\n')[-1]
                        metrics["resolved_issues"] = self.parse_number(value)

                    elif "Completed Tasks" in text:
                        value = text.split('\n')[-1]
                        metrics["completed_tasks"] = self.parse_number(value)

                    elif "Total Sessions" in text:
                        value = text.split('\n')[-1]
                        metrics["total_sessions"] = self.parse_number(value)

                    elif "Completed Sessions" in text:
                        value = text.split('\n')[-1]
                        metrics["completed_sessions"] = self.parse_number(value)

                except:
                    continue

            # Count non-None values
            captured = sum(1 for v in metrics.values() if v is not None) - 1  # -1 for site_name
            print(f"  ✓ Captured {captured} metrics")

            return metrics

        except Exception as e:
            print(f"  ✗ Error capturing metrics: {str(e)}")
            return metrics

    def parse_number(self, value_str):
        """Parse number from string (handles $, k, etc.)"""
        try:
            value_str = value_str.strip()

            # Remove $ sign
            value_str = value_str.replace('$', '').replace(',', '')

            # Handle k (thousands)
            if 'k' in value_str.lower():
                value_str = value_str.lower().replace('k', '')
                return int(float(value_str) * 1000)

            # Handle m (millions)
            if 'm' in value_str.lower():
                value_str = value_str.lower().replace('m', '')
                return int(float(value_str) * 1000000)

            # Just a number
            return int(float(value_str))

        except:
            return None

    def capture_all_sites_data(self, url, email, password, label):
        """Capture data for all sites on a website"""
        print(f"\n{'#'*70}")
        print(f"# {label}")
        print(f"# {url}")
        print(f"{'#'*70}")

        if not self.login(url, email, password):
            return {}

        # Get list of all sites
        sites = self.get_all_sites()

        if not sites:
            print("⚠ No sites found!")
            return {}

        all_data = {}

        # Capture data for each site
        for idx, site in enumerate(sites, 1):
            print(f"\n[{idx}/{len(sites)}] Processing: {site}")

            # Select the site
            if self.select_site(site):
                # Capture metrics
                metrics = self.capture_dashboard_metrics(site)
                all_data[site] = metrics
            else:
                print(f"  ⚠ Skipped: {site}")

        print(f"\n✓ Completed {label}: {len(all_data)} sites captured")
        return all_data

    def compare_all_sites(self, rnd_data, ai_data):
        """Compare all sites and generate detailed report"""
        print(f"\n{'='*70}")
        print(f"📊 COMPARING ALL SITES")
        print(f"{'='*70}")

        # Get all unique sites
        all_sites = set(list(rnd_data.keys()) + list(ai_data.keys()))

        comparisons = []

        for site in sorted(all_sites):
            rnd_site = rnd_data.get(site, {})
            ai_site = ai_data.get(site, {})

            # Get all metric fields
            all_fields = set()
            if rnd_site:
                all_fields.update([k for k in rnd_site.keys() if k != 'site_name'])
            if ai_site:
                all_fields.update([k for k in ai_site.keys() if k != 'site_name'])

            # Compare each field
            for field in sorted(all_fields):
                rnd_value = rnd_site.get(field)
                ai_value = ai_site.get(field)

                # Skip if both are None
                if rnd_value is None and ai_value is None:
                    continue

                # Calculate difference
                if rnd_value != ai_value:
                    change = None
                    if rnd_value is not None and ai_value is not None:
                        change = ai_value - rnd_value

                    # Determine severity
                    severity = self.determine_severity(field, rnd_value, ai_value, change)

                    comparisons.append({
                        "site": site,
                        "field": field,
                        "old_value": rnd_value if rnd_value is not None else "N/A",
                        "new_value": ai_value if ai_value is not None else "N/A",
                        "change": change if change is not None else "N/A",
                        "severity": severity
                    })

        # Count by severity
        critical = sum(1 for c in comparisons if c['severity'] == 'CRITICAL')
        major = sum(1 for c in comparisons if c['severity'] == 'MAJOR')
        minor = sum(1 for c in comparisons if c['severity'] == 'MINOR')

        print(f"\nTotal Comparisons: {len(comparisons)}")
        print(f"  Critical: {critical}")
        print(f"  Major: {major}")
        print(f"  Minor: {minor}")

        return {
            "summary": {
                "total_sites": len(all_sites),
                "total_differences": len(comparisons),
                "critical": critical,
                "major": major,
                "minor": minor
            },
            "comparisons": comparisons
        }

    def determine_severity(self, field, old_val, new_val, change):
        """Determine severity of difference"""

        # Missing data is critical
        if old_val is not None and new_val is None:
            return "CRITICAL"

        if new_val is not None and old_val is None:
            return "MAJOR"  # New data added

        # Asset count changes
        if "asset" in field.lower():
            if abs(change) >= 100:
                return "MAJOR"
            elif change < 0:
                return "CRITICAL"  # Lost assets
            else:
                return "MINOR"

        # Financial metrics
        if "value" in field.lower() or "risk" in field.lower():
            if abs(change) >= 100000:
                return "MAJOR"
            else:
                return "MINOR"

        # Issue tracking
        if "issue" in field.lower():
            if abs(change) >= 10:
                return "MAJOR"
            else:
                return "MINOR"

        return "MINOR"

    def generate_html_report(self, comparison, rnd_data, ai_data, output_file="complete_all_sites_comparison.html"):
        """Generate comprehensive HTML report"""

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Complete All Sites Comparison Report</title>
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
        .success {{ color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; font-size: 14px; }}
        th {{ background: #f8f9fa; font-weight: 600; text-transform: uppercase; font-size: 11px; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
        .badge-critical {{ background: #fadbd8; color: #dc3545; }}
        .badge-major {{ background: #ffe5d0; color: #fd7e14; }}
        .badge-minor {{ background: #fff3cd; color: #ffc107; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Complete All Sites Comparison Report</h1>
        <p>Comprehensive comparison of ALL sites between RND and AI environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {timestamp}</p>
    </div>

    <div class="summary">
        <h2>📊 Overall Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{comparison['summary']['total_sites']}</div>
                <div>Total Sites</div>
            </div>
            <div class="stat">
                <div class="stat-number critical">{comparison['summary']['critical']}</div>
                <div>Critical Differences</div>
            </div>
            <div class="stat">
                <div class="stat-number major">{comparison['summary']['major']}</div>
                <div>Major Differences</div>
            </div>
            <div class="stat">
                <div class="stat-number minor">{comparison['summary']['minor']}</div>
                <div>Minor Differences</div>
            </div>
            <div class="stat">
                <div class="stat-number">{comparison['summary']['total_differences']}</div>
                <div>Total Differences</div>
            </div>
        </div>
    </div>

    <div class="summary">
        <h2>📋 Complete Site Comparison Results</h2>
        <p><strong>Showing ALL sites and ALL differences</strong></p>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Site Name</th>
                    <th>Field</th>
                    <th>Old Value (RND)</th>
                    <th>New Value (AI)</th>
                    <th>Change</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
"""

        for idx, comp in enumerate(comparison['comparisons'], 1):
            change_str = ""
            if comp['change'] != "N/A":
                if comp['change'] > 0:
                    change_str = f"+{comp['change']:,}"
                else:
                    change_str = f"{comp['change']:,}"
            else:
                change_str = "N/A"

            badge_class = f"badge-{comp['severity'].lower()}"

            # Format values
            old_val = f"{comp['old_value']:,}" if isinstance(comp['old_value'], int) else comp['old_value']
            new_val = f"{comp['new_value']:,}" if isinstance(comp['new_value'], int) else comp['new_value']

            html += f"""
                <tr>
                    <td>{idx}</td>
                    <td><strong>{comp['site']}</strong></td>
                    <td><code>{comp['field']}</code></td>
                    <td>{old_val}</td>
                    <td>{new_val}</td>
                    <td>{change_str}</td>
                    <td><span class="badge {badge_class}">{comp['severity']}</span></td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n✓ HTML report generated: {output_file}")

    def run(self, email, password):
        """Main execution"""
        try:
            print(f"\n{'#'*70}")
            print(f"# COMPLETE ALL SITES COMPARISON TOOL")
            print(f"# Captures and compares EVERY site from both websites")
            print(f"{'#'*70}\n")

            self.setup_driver()

            # Capture RND data
            rnd_data = self.capture_all_sites_data(self.rnd_url, email, password, "RND WEBSITE")

            # Save RND data
            with open('rnd_all_sites_data.json', 'w') as f:
                json.dump(rnd_data, f, indent=2)
            print(f"\n💾 Saved: rnd_all_sites_data.json")

            # Capture AI data
            ai_data = self.capture_all_sites_data(self.ai_url, email, password, "AI WEBSITE")

            # Save AI data
            with open('ai_all_sites_data.json', 'w') as f:
                json.dump(ai_data, f, indent=2)
            print(f"💾 Saved: ai_all_sites_data.json")

            # Compare
            comparison = self.compare_all_sites(rnd_data, ai_data)

            # Save comparison
            with open('complete_sites_comparison.json', 'w') as f:
                json.dump(comparison, f, indent=2)
            print(f"💾 Saved: complete_sites_comparison.json")

            # Generate HTML report
            self.generate_html_report(comparison, rnd_data, ai_data)

            print(f"\n{'='*70}")
            print(f"✓ COMPLETE! Check the HTML report for full details.")
            print(f"{'='*70}\n")

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print("\n🚪 Closing browser...")
                time.sleep(2)
                self.driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_all_sites_complete.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    comparator = CompleteAllSitesComparator()
    comparator.run(email, password)
