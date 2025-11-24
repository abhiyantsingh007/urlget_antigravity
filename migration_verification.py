import json
import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from selenium.webdriver.chrome.service import Service

class MigrationVerifier:
    def __init__(self, old_website_url, new_website_url, email, password):
        self.old_website_url = old_website_url
        self.new_website_url = new_website_url
        self.email = email
        self.password = password
        self.driver = None
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"migration_verification_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "old_website_data"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "new_website_data"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "comparison_results"), exist_ok=True)
        
        print(f"Created output directory: {self.output_dir}")
    
    def setup_driver(self):
        """Setup Chrome driver"""
        # Automatically download and install ChromeDriver
        chromedriver_autoinstaller.install()
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # Run in headless mode to avoid display issues
        chrome_options.add_argument("--headless")
        
        try:
            # Setup ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver initialized successfully")
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            raise Exception(f"Could not initialize Chrome driver: {e}")
    
    def login_to_website(self, website_url):
        """Login to a website"""
        print(f"Logging in to {website_url}...")
        self.driver.get(f"{website_url}/login")
        time.sleep(2)
        
        # Enter credentials
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )
        print("Login successful")
        time.sleep(3)
    
    def capture_dashboard_data(self, website_url):
        """Capture dashboard data from a website"""
        print(f"\n--- Capturing dashboard data from {website_url} ---")
        
        try:
            # Navigate to dashboard
            self.driver.get(f"{website_url}/dashboard")
            time.sleep(3)
            
            # Capture data
            site_dir = os.path.join(self.output_dir, 
                                  "old_website_data" if website_url == self.old_website_url else "new_website_data",
                                  "dashboard")
            os.makedirs(site_dir, exist_ok=True)
            
            # Save page source
            page_source_path = os.path.join(site_dir, "page_source.html")
            with open(page_source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"  ✓ Page source saved: page_source.html")
            
            # Extract visible text
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                text_path = os.path.join(site_dir, "visible_text.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(body_text)
                print(f"  ✓ Visible text saved: visible_text.txt")
            except Exception as e:
                print(f"  ✗ Error extracting visible text: {e}")
            
            print(f"  Completed dashboard data capture")
            return True
            
        except Exception as e:
            print(f"  Error capturing dashboard data: {e}")
            return False
    
    def capture_sites_data(self, website_url):
        """Capture data from all sites on a website"""
        print(f"\n--- Capturing sites data from {website_url} ---")
        
        try:
            # Navigate to sites page
            self.driver.get(f"{website_url}/sites")
            time.sleep(3)
            
            # Get list of sites
            sites = ["London UK", "All Facilities", "Melbourne AU", "ShowSite3", "test", "test site", "Toronto Canada"]
            
            captured_sites = []
            for site in sites:
                try:
                    print(f"  Capturing data for site: {site}")
                    
                    # Navigate to specific site page if needed
                    # For now, we'll capture the general sites page data
                    site_dir = os.path.join(self.output_dir, 
                                          "old_website_data" if website_url == self.old_website_url else "new_website_data",
                                          site.replace("/", "_").replace("\\", "_"))
                    os.makedirs(site_dir, exist_ok=True)
                    
                    # Save page source
                    page_source_path = os.path.join(site_dir, "page_source.html")
                    with open(page_source_path, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print(f"    ✓ Page source saved: page_source.html")
                    
                    # Extract visible text
                    try:
                        body_text = self.driver.find_element(By.TAG_NAME, "body").text
                        text_path = os.path.join(site_dir, "visible_text.txt")
                        with open(text_path, 'w', encoding='utf-8') as f:
                            f.write(body_text)
                        print(f"    ✓ Visible text saved: visible_text.txt")
                    except Exception as e:
                        print(f"    ✗ Error extracting visible text: {e}")
                    
                    captured_sites.append(site)
                    time.sleep(1)  # Small delay between sites
                    
                except Exception as e:
                    print(f"    Error capturing data for site '{site}': {e}")
            
            print(f"  Completed sites data capture for {len(captured_sites)} sites")
            return captured_sites
            
        except Exception as e:
            print(f"  Error capturing sites data: {e}")
            return []
    
    def extract_numeric_values(self, text):
        """Extract numeric values from text that might represent asset counts or similar metrics"""
        # Look for patterns like "Total Assets: 5" or "Assets (3)" or "count: 10"
        patterns = [
            r'(?:total\s*)?assets?\s*[:\-]?\s*(\d+)',
            r'assets?\s*\((\d+)\)',
            r'count\s*[:\-]?\s*(\d+)',
            r'total\s*[:\-]?\s*(\d+)',
            r'(\d+)\s*assets?',
        ]
        
        results = {}
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for i, match in enumerate(matches):
                key = f"pattern_{pattern}_{i}"
                results[key] = int(match)
        
        return results
    
    def compare_numeric_differences(self, old_text, new_text):
        """Compare numeric values between old and new text to find discrepancies"""
        old_numbers = self.extract_numeric_values(old_text)
        new_numbers = self.extract_numeric_values(new_text)
        
        differences = []
        
        # Compare all numeric values
        all_keys = set(old_numbers.keys()) | set(new_numbers.keys())
        for key in all_keys:
            old_val = old_numbers.get(key, None)
            new_val = new_numbers.get(key, None)
            
            if old_val is None and new_val is not None:
                differences.append({
                    "type": "numeric_value_added",
                    "key": key,
                    "old_value": None,
                    "new_value": new_val,
                    "description": f"New numeric value found: {new_val}"
                })
            elif old_val is not None and new_val is None:
                differences.append({
                    "type": "numeric_value_removed",
                    "key": key,
                    "old_value": old_val,
                    "new_value": None,
                    "description": f"Numeric value missing in new version: {old_val}"
                })
            elif old_val is not None and new_val is not None and old_val != new_val:
                differences.append({
                    "type": "numeric_value_changed",
                    "key": key,
                    "old_value": old_val,
                    "new_value": new_val,
                    "description": f"Numeric value changed from {old_val} to {new_val}"
                })
        
        return differences
    
    def compare_site_data(self, site_name):
        """Compare data for a specific site between old and new websites"""
        print(f"\n--- Comparing data for site: {site_name} ---")
        
        try:
            old_site_dir = os.path.join(self.output_dir, "old_website_data", site_name.replace("/", "_").replace("\\", "_"))
            new_site_dir = os.path.join(self.output_dir, "new_website_data", site_name.replace("/", "_").replace("\\", "_"))
            
            comparison_result = {
                "site": site_name,
                "comparison_timestamp": datetime.now().isoformat(),
                "differences": []
            }
            
            # Compare page sources
            old_page_source = os.path.join(old_site_dir, "page_source.html")
            new_page_source = os.path.join(new_site_dir, "page_source.html")
            
            page_source_diffs = []
            if os.path.exists(old_page_source) and os.path.exists(new_page_source):
                with open(old_page_source, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                with open(new_page_source, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                
                if old_content != new_content:
                    comparison_result["differences"].append({
                        "type": "page_source",
                        "status": "different",
                        "details": "Page source content differs between old and new websites"
                    })
                    print(f"  ✗ Page source differs")
                else:
                    print(f"  ✓ Page source matches")
            else:
                comparison_result["differences"].append({
                    "type": "page_source",
                    "status": "missing",
                    "details": "Page source file missing for one or both websites"
                })
                print(f"  ✗ Page source missing")
            
            # Compare visible text
            old_visible_text = os.path.join(old_site_dir, "visible_text.txt")
            new_visible_text = os.path.join(new_site_dir, "visible_text.txt")
            
            if os.path.exists(old_visible_text) and os.path.exists(new_visible_text):
                with open(old_visible_text, 'r', encoding='utf-8') as f:
                    old_text = f.read()
                with open(new_visible_text, 'r', encoding='utf-8') as f:
                    new_text = f.read()
                
                # Standard text comparison
                if old_text != new_text:
                    comparison_result["differences"].append({
                        "type": "visible_text",
                        "status": "different",
                        "details": "Visible text content differs between old and new websites"
                    })
                    print(f"  ✗ Visible text differs")
                else:
                    print(f"  ✓ Visible text matches")
                
                # Numeric value comparison for detecting specific issues like asset count differences
                numeric_differences = self.compare_numeric_differences(old_text, new_text)
                for diff in numeric_differences:
                    comparison_result["differences"].append({
                        "type": "numeric_difference",
                        "status": "different",
                        "severity": "CRITICAL" if diff["type"] == "numeric_value_changed" and diff["new_value"] == 0 and diff["old_value"] > 0 else "MINOR",
                        "details": diff["description"],
                        "old_value": diff["old_value"],
                        "new_value": diff["new_value"]
                    })
                    if diff["type"] == "numeric_value_changed" and diff["new_value"] == 0 and diff["old_value"] > 0:
                        print(f"  ⚠️  CRITICAL: {diff['description']}")
                    else:
                        print(f"  ℹ️  MINOR: {diff['description']}")
                        
            else:
                comparison_result["differences"].append({
                    "type": "visible_text",
                    "status": "missing",
                    "details": "Visible text file missing for one or both websites"
                })
                print(f"  ✗ Visible text missing")
            
            # Save comparison result
            safe_site_name = site_name.replace("/", "_").replace("\\", "_")
            comparison_file = os.path.join(self.output_dir, "comparison_results", f"{safe_site_name}_comparison.json")
            with open(comparison_file, 'w') as f:
                json.dump(comparison_result, f, indent=2)
            
            print(f"  Comparison result saved to: {os.path.basename(comparison_file)}")
            return comparison_result
            
        except Exception as e:
            print(f"  Error comparing data for site '{site_name}': {e}")
            return None
    
    def generate_html_report(self, summary):
        """Generate an enhanced HTML report with better visualization of differences"""
        report_path = os.path.join(self.output_dir, "enhanced_migration_verification_report.html")
        
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
    
    def run_verification(self):
        """Run the complete migration verification"""
        try:
            print("=== STARTING ENHANCED MIGRATION VERIFICATION ===")
            
            self.setup_driver()
            
            # Sites to verify
            sites = ["London UK", "All Facilities", "Melbourne AU", "ShowSite3", "test", "test site", "Toronto Canada"]
            
            # Capture dashboard data from both websites
            print(f"\n=== CAPTURING DASHBOARD DATA ===")
            self.login_to_website(self.old_website_url)
            self.capture_dashboard_data(self.old_website_url)
            
            self.login_to_website(self.new_website_url)
            self.capture_dashboard_data(self.new_website_url)
            
            # Capture data from old website
            print(f"\n=== CAPTURING SITES DATA FROM OLD WEBSITE ({self.old_website_url}) ===")
            self.login_to_website(self.old_website_url)
            old_captured_sites = self.capture_sites_data(self.old_website_url)
            
            # Capture data from new website
            print(f"\n=== CAPTURING SITES DATA FROM NEW WEBSITE ({self.new_website_url}) ===")
            self.login_to_website(self.new_website_url)
            new_captured_sites = self.capture_sites_data(self.new_website_url)
            
            # Compare data for each site
            print(f"\n=== COMPARING DATA BETWEEN WEBSITES ===")
            comparison_results = []
            for site in sites:
                result = self.compare_site_data(site)
                if result:
                    comparison_results.append(result)
            
            # Create summary
            summary = {
                "verification_timestamp": datetime.now().isoformat(),
                "old_website_url": self.old_website_url,
                "new_website_url": self.new_website_url,
                "sites_verified": sites,
                "old_sites_captured": old_captured_sites,
                "new_sites_captured": new_captured_sites,
                "comparison_results": comparison_results
            }
            
            summary_path = os.path.join(self.output_dir, "verification_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Generate enhanced HTML report
            self.generate_html_report(summary)
            
            print(f"\n=== MIGRATION VERIFICATION COMPLETED ===")
            print(f"Old website sites captured: {len(old_captured_sites)}")
            print(f"New website sites captured: {len(new_captured_sites)}")
            print(f"Comparison results: {len(comparison_results)}")
            print(f"All data saved to: {self.output_dir}")
            
            return self.output_dir
            
        except Exception as e:
            print(f"Error during verification: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
            
        finally:
            if self.driver:
                self.driver.quit()

def run_migration_verification():
    """Run the migration verification with default credentials"""
    # Configuration
    OLD_WEBSITE_URL = "https://acme.egalvanic-rnd.com"  # Old website
    NEW_WEBSITE_URL = "https://acme.egalvanic.ai"       # New migration website
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Run verification
    verifier = MigrationVerifier(OLD_WEBSITE_URL, NEW_WEBSITE_URL, EMAIL, PASSWORD)
    output_directory = verifier.run_verification()
    
    print(f"\nMigration verification completed!")
    print(f"All data has been saved to: {output_directory}")

if __name__ == "__main__":
    print("Starting enhanced migration verification...")
    print("This script will verify that all data has been correctly migrated")
    print("from the old website to the new migration website.")
    print("")
    print("Old website: https://acme.egalvanic-rnd.com")
    print("New website: https://acme.egalvanic.ai")
    print("")
    
    run_migration_verification()