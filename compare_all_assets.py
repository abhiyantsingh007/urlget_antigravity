"""
Complete Asset Comparison Script
Captures all assets from both RND and AI websites and generates a detailed comparison report
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import sys

class AssetComparator:
    def __init__(self):
        self.rnd_url = "https://acme.egalvanic-rnd.com"
        self.ai_url = "https://acme.egalvanic.ai"
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Remove headless mode to allow login
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def login(self, url, email, password):
        """Login to the website"""
        print(f"\n{'='*60}")
        print(f"Logging into: {url}")
        print(f"{'='*60}")

        self.driver.get(f"{url}/login")
        time.sleep(3)

        try:
            # Wait for email field
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            print(f"✓ Entered email: {email}")

            # Find and fill password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            print(f"✓ Entered password")

            # Click sign in button
            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()
            print(f"✓ Clicked Sign In")

            # Wait for dashboard to load
            time.sleep(8)

            # Check if we're on dashboard
            current_url = self.driver.current_url
            if "dashboard" in current_url or "site" in current_url:
                print(f"✓ Login successful!")
                return True
            else:
                print(f"⚠ Unexpected URL after login: {current_url}")
                return False

        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def select_site(self, site_name):
        """Select a specific site from dropdown"""
        print(f"\n📍 Selecting site: {site_name}")

        try:
            # Click on site selector dropdown
            site_selector = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='site-selector'], .site-selector, button:has-text('Site')"))
            )
            site_selector.click()
            time.sleep(2)

            # Find and click the specific site
            site_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{site_name}')] | //li[contains(text(), '{site_name}')] | //span[contains(text(), '{site_name}')]"))
            )
            site_option.click()
            time.sleep(3)
            print(f"✓ Selected site: {site_name}")
            return True

        except Exception as e:
            print(f"✗ Could not select site '{site_name}': {str(e)}")
            return False

    def navigate_to_assets(self):
        """Navigate to the Assets page"""
        print(f"\n🔍 Navigating to Assets page...")

        try:
            # Look for Assets link in navigation
            assets_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Assets')] | //nav//span[contains(text(), 'Assets')]"))
            )
            assets_link.click()
            time.sleep(3)
            print(f"✓ Navigated to Assets page")
            return True

        except Exception as e:
            print(f"✗ Could not navigate to Assets: {str(e)}")
            # Try direct URL
            current_url = self.driver.current_url
            base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url.split('/site')[0]
            assets_url = f"{base_url}/assets"
            print(f"  Trying direct URL: {assets_url}")
            self.driver.get(assets_url)
            time.sleep(3)
            return True

    def get_total_asset_count(self):
        """Get the total number of assets from the page"""
        try:
            # Look for pagination text like "1-25 of 179"
            pagination_text = self.driver.find_element(By.XPATH, "//*[contains(text(), 'of ')]").text
            total = int(pagination_text.split('of ')[-1].strip())
            print(f"✓ Total assets found: {total}")
            return total
        except Exception as e:
            print(f"⚠ Could not get total count: {str(e)}")
            return 0

    def set_rows_per_page(self, rows=100):
        """Set the number of rows per page to maximum"""
        print(f"\n⚙ Setting rows per page to {rows}...")

        try:
            # Click on rows per page dropdown
            rows_dropdown = self.driver.find_element(By.XPATH, "//select[contains(@aria-label, 'Rows per page')] | //*[contains(text(), 'Rows per page')]/following-sibling::*")
            rows_dropdown.click()
            time.sleep(1)

            # Select maximum rows
            max_option = self.driver.find_element(By.XPATH, f"//option[@value='{rows}'] | //li[contains(text(), '{rows}')]")
            max_option.click()
            time.sleep(2)
            print(f"✓ Set to {rows} rows per page")
            return True

        except Exception as e:
            print(f"⚠ Could not change rows per page: {str(e)}")
            return False

    def extract_assets_from_current_page(self):
        """Extract all assets from the current page"""
        assets = []

        try:
            # Wait for table to load
            time.sleep(2)

            # Find all asset rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr, [role='row']")

            for row in rows:
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td, [role='cell']")

                    if len(cells) >= 4:
                        asset = {
                            "asset_name": cells[0].text.strip(),
                            "qr_code": cells[1].text.strip(),
                            "condition": cells[2].text.strip(),
                            "asset_class": cells[3].text.strip(),
                            "building": cells[4].text.strip() if len(cells) > 4 else ""
                        }

                        # Only add if asset name is not empty
                        if asset["asset_name"] and asset["asset_name"] != "—":
                            assets.append(asset)

                except Exception as e:
                    continue

            print(f"  Extracted {len(assets)} assets from current page")
            return assets

        except Exception as e:
            print(f"✗ Error extracting assets: {str(e)}")
            return []

    def click_next_page(self):
        """Click the next page button"""
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next page'], button:has-text('Next')")

            if next_button.is_enabled():
                next_button.click()
                time.sleep(2)
                return True
            else:
                return False

        except Exception as e:
            return False

    def capture_all_assets(self, site_name):
        """Capture all assets for a site by paginating through all pages"""
        print(f"\n{'='*60}")
        print(f"📦 Capturing ALL assets for: {site_name}")
        print(f"{'='*60}")

        all_assets = []

        # Get total count
        total_count = self.get_total_asset_count()

        # Try to set max rows per page
        self.set_rows_per_page(100)

        page_num = 1
        while True:
            print(f"\n📄 Processing page {page_num}...")

            # Extract assets from current page
            assets = self.extract_assets_from_current_page()
            all_assets.extend(assets)

            print(f"  Total assets captured so far: {len(all_assets)}")

            # Check if we have all assets
            if len(all_assets) >= total_count:
                print(f"\n✓ Captured all {len(all_assets)} assets!")
                break

            # Try to go to next page
            if not self.click_next_page():
                print(f"\n✓ No more pages. Captured {len(all_assets)} assets total.")
                break

            page_num += 1

            # Safety limit
            if page_num > 20:
                print(f"\n⚠ Reached page limit. Stopping.")
                break

        return all_assets

    def capture_site_assets(self, url, site_name, label):
        """Capture assets from a specific site"""
        print(f"\n{'#'*60}")
        print(f"# {label}: {url}")
        print(f"{'#'*60}")

        # Navigate to assets page
        self.navigate_to_assets()

        # Select the site
        if not self.select_site(site_name):
            print(f"⚠ Warning: Could not select site. Will capture current site's assets.")

        # Capture all assets
        assets = self.capture_all_assets(site_name)

        return assets

    def compare_assets(self, rnd_assets, ai_assets):
        """Compare assets between RND and AI sites"""
        print(f"\n{'='*60}")
        print(f"📊 COMPARISON ANALYSIS")
        print(f"{'='*60}")

        # Create asset name sets
        rnd_names = {asset['asset_name'] for asset in rnd_assets}
        ai_names = {asset['asset_name'] for asset in ai_assets}

        # Find differences
        only_in_rnd = rnd_names - ai_names
        only_in_ai = ai_names - rnd_names
        common = rnd_names & ai_names

        # Create detailed comparison
        comparison = {
            "summary": {
                "rnd_total": len(rnd_assets),
                "ai_total": len(ai_assets),
                "common_assets": len(common),
                "only_in_rnd": len(only_in_rnd),
                "only_in_ai": len(only_in_ai),
                "difference": len(ai_assets) - len(rnd_assets)
            },
            "assets_only_in_rnd": sorted(list(only_in_rnd)),
            "assets_only_in_ai": sorted(list(only_in_ai)),
            "common_assets": sorted(list(common)),
            "field_differences": []
        }

        # Compare field values for common assets
        rnd_dict = {asset['asset_name']: asset for asset in rnd_assets}
        ai_dict = {asset['asset_name']: asset for asset in ai_assets}

        for asset_name in common:
            rnd_asset = rnd_dict[asset_name]
            ai_asset = ai_dict[asset_name]

            differences = {}
            for field in ['qr_code', 'condition', 'asset_class', 'building']:
                rnd_value = rnd_asset.get(field, '')
                ai_value = ai_asset.get(field, '')

                if rnd_value != ai_value:
                    differences[field] = {
                        "rnd": rnd_value,
                        "ai": ai_value
                    }

            if differences:
                comparison["field_differences"].append({
                    "asset_name": asset_name,
                    "differences": differences
                })

        return comparison

    def generate_html_report(self, comparison, rnd_assets, ai_assets, output_file="asset_comparison_report.html"):
        """Generate a detailed HTML comparison report"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Asset Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .critical {{ color: #dc3545; }}
        .warning {{ color: #fd7e14; }}
        .success {{ color: #28a745; }}
        .info {{ color: #0dcaf0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; text-transform: uppercase; font-size: 12px; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
        .badge-danger {{ background: #fadbd8; color: #dc3545; }}
        .badge-success {{ background: #d1f2eb; color: #28a745; }}
        .badge-warning {{ background: #fff3cd; color: #fd7e14; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
        .diff {{ background: #fff3cd; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Complete Asset Comparison Report</h1>
        <p>Comprehensive comparison of all assets between RND and AI environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>📊 Summary Statistics</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number info">{comparison['summary']['rnd_total']}</div>
                <div>RND Assets</div>
            </div>
            <div class="stat">
                <div class="stat-number info">{comparison['summary']['ai_total']}</div>
                <div>AI Assets</div>
            </div>
            <div class="stat">
                <div class="stat-number success">{comparison['summary']['common_assets']}</div>
                <div>Common Assets</div>
            </div>
            <div class="stat">
                <div class="stat-number {'critical' if comparison['summary']['only_in_rnd'] > 0 else 'success'}">{comparison['summary']['only_in_rnd']}</div>
                <div>Only in RND</div>
            </div>
            <div class="stat">
                <div class="stat-number {'warning' if comparison['summary']['only_in_ai'] > 0 else 'success'}">{comparison['summary']['only_in_ai']}</div>
                <div>Only in AI</div>
            </div>
            <div class="stat">
                <div class="stat-number {'warning' if len(comparison['field_differences']) > 0 else 'success'}">{len(comparison['field_differences'])}</div>
                <div>Field Differences</div>
            </div>
        </div>
    </div>
"""

        # Assets only in RND
        if comparison['assets_only_in_rnd']:
            html += f"""
    <div class="section">
        <h2>🔴 Assets Only in RND ({len(comparison['assets_only_in_rnd'])} assets)</h2>
        <p><strong>These assets are missing in the AI website:</strong></p>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Asset Name</th>
                    <th>Asset Class</th>
                    <th>Building</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
            rnd_dict = {asset['asset_name']: asset for asset in rnd_assets}
            for idx, asset_name in enumerate(comparison['assets_only_in_rnd'], 1):
                asset = rnd_dict.get(asset_name, {})
                html += f"""
                <tr>
                    <td>{idx}</td>
                    <td><strong>{asset_name}</strong></td>
                    <td>{asset.get('asset_class', '—')}</td>
                    <td>{asset.get('building', '—')}</td>
                    <td><span class="badge badge-danger">MISSING IN AI</span></td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""

        # Assets only in AI
        if comparison['assets_only_in_ai']:
            html += f"""
    <div class="section">
        <h2>🟢 Assets Only in AI ({len(comparison['assets_only_in_ai'])} assets)</h2>
        <p><strong>These assets are new in the AI website:</strong></p>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Asset Name</th>
                    <th>Asset Class</th>
                    <th>Building</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
            ai_dict = {asset['asset_name']: asset for asset in ai_assets}
            for idx, asset_name in enumerate(comparison['assets_only_in_ai'], 1):
                asset = ai_dict.get(asset_name, {})
                html += f"""
                <tr>
                    <td>{idx}</td>
                    <td><strong>{asset_name}</strong></td>
                    <td>{asset.get('asset_class', '—')}</td>
                    <td>{asset.get('building', '—')}</td>
                    <td><span class="badge badge-success">NEW IN AI</span></td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""

        # Field differences
        if comparison['field_differences']:
            html += f"""
    <div class="section">
        <h2>⚠️ Assets with Field Differences ({len(comparison['field_differences'])} assets)</h2>
        <p><strong>These assets exist in both sites but have different field values:</strong></p>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Asset Name</th>
                    <th>Field</th>
                    <th>RND Value</th>
                    <th>AI Value</th>
                </tr>
            </thead>
            <tbody>
"""
            for idx, item in enumerate(comparison['field_differences'], 1):
                asset_name = item['asset_name']
                differences = item['differences']

                first_field = True
                for field, values in differences.items():
                    html += f"""
                <tr>
                    <td>{"" if not first_field else idx}</td>
                    <td>{"" if not first_field else f"<strong>{asset_name}</strong>"}</td>
                    <td><code>{field}</code></td>
                    <td>{values['rnd'] if values['rnd'] else '—'}</td>
                    <td class="diff">{values['ai'] if values['ai'] else '—'}</td>
                </tr>
"""
                    first_field = False

            html += """
            </tbody>
        </table>
    </div>
"""

        # Common assets summary
        html += f"""
    <div class="section">
        <h2>✅ Common Assets ({len(comparison['common_assets'])} assets)</h2>
        <p><strong>These assets exist in both RND and AI websites with identical data.</strong></p>
        <p style="color: #6c757d; font-size: 14px;">Click to expand and view the complete list:</p>
        <details>
            <summary style="cursor: pointer; padding: 10px; background: #f8f9fa; border-radius: 5px; margin: 10px 0;">
                <strong>View all {len(comparison['common_assets'])} common assets</strong>
            </summary>
            <div style="margin-top: 15px; max-height: 400px; overflow-y: auto;">
                <ul style="columns: 3; column-gap: 20px; list-style-type: disc; padding-left: 20px;">
"""
        for asset_name in comparison['common_assets']:
            html += f"                    <li>{asset_name}</li>\n"

        html += """
                </ul>
            </div>
        </details>
    </div>

    <div class="section">
        <h2>📝 Recommendations</h2>
        <ul>
"""

        if comparison['summary']['only_in_rnd'] > 0:
            html += f"""            <li><strong>Critical:</strong> {comparison['summary']['only_in_rnd']} assets are missing in the AI website. These need to be migrated immediately.</li>\n"""

        if comparison['summary']['only_in_ai'] > 0:
            html += f"""            <li><strong>Info:</strong> {comparison['summary']['only_in_ai']} new assets found in the AI website. Verify these are intentional additions.</li>\n"""

        if len(comparison['field_differences']) > 0:
            html += f"""            <li><strong>Warning:</strong> {len(comparison['field_differences'])} assets have field differences. Review these for data consistency.</li>\n"""

        if comparison['summary']['only_in_rnd'] == 0 and comparison['summary']['only_in_ai'] == 0 and len(comparison['field_differences']) == 0:
            html += """            <li><strong>Success:</strong> All assets match perfectly between RND and AI websites! ✨</li>\n"""

        html += """
        </ul>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n✓ HTML report generated: {output_file}")
        return output_file

    def save_results(self, rnd_assets, ai_assets, comparison):
        """Save results to JSON files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save RND assets
        rnd_file = f"rnd_all_assets_{timestamp}.json"
        with open(rnd_file, 'w', encoding='utf-8') as f:
            json.dump(rnd_assets, f, indent=2)
        print(f"✓ Saved RND assets: {rnd_file}")

        # Save AI assets
        ai_file = f"ai_all_assets_{timestamp}.json"
        with open(ai_file, 'w', encoding='utf-8') as f:
            json.dump(ai_assets, f, indent=2)
        print(f"✓ Saved AI assets: {ai_file}")

        # Save comparison
        comparison_file = f"asset_comparison_{timestamp}.json"
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        print(f"✓ Saved comparison: {comparison_file}")

        return rnd_file, ai_file, comparison_file

    def run(self, email, password, site_name):
        """Main execution method"""
        try:
            print(f"\n{'#'*60}")
            print(f"# COMPLETE ASSET COMPARISON TOOL")
            print(f"{'#'*60}")
            print(f"Site to compare: {site_name}")
            print(f"Email: {email}")
            print(f"{'#'*60}\n")

            # Setup driver
            self.setup_driver()

            # Capture RND assets
            self.driver.get(self.rnd_url)
            time.sleep(3)

            if not self.login(self.rnd_url, email, password):
                print("✗ Failed to login to RND site")
                return

            rnd_assets = self.capture_site_assets(self.rnd_url, site_name, "RND WEBSITE")

            print(f"\n{'='*60}")
            print(f"RND Website: Captured {len(rnd_assets)} assets")
            print(f"{'='*60}")

            # Capture AI assets
            self.driver.get(self.ai_url)
            time.sleep(3)

            if not self.login(self.ai_url, email, password):
                print("✗ Failed to login to AI site")
                return

            ai_assets = self.capture_site_assets(self.ai_url, site_name, "AI WEBSITE")

            print(f"\n{'='*60}")
            print(f"AI Website: Captured {len(ai_assets)} assets")
            print(f"{'='*60}")

            # Compare assets
            comparison = self.compare_assets(rnd_assets, ai_assets)

            # Print summary
            print(f"\n{'='*60}")
            print(f"COMPARISON SUMMARY")
            print(f"{'='*60}")
            print(f"RND Total:        {comparison['summary']['rnd_total']}")
            print(f"AI Total:         {comparison['summary']['ai_total']}")
            print(f"Difference:       {comparison['summary']['difference']:+d}")
            print(f"Common Assets:    {comparison['summary']['common_assets']}")
            print(f"Only in RND:      {comparison['summary']['only_in_rnd']}")
            print(f"Only in AI:       {comparison['summary']['only_in_ai']}")
            print(f"Field Diffs:      {len(comparison['field_differences'])}")
            print(f"{'='*60}")

            # Save results
            self.save_results(rnd_assets, ai_assets, comparison)

            # Generate HTML report
            html_file = self.generate_html_report(comparison, rnd_assets, ai_assets)

            print(f"\n{'='*60}")
            print(f"✓ COMPARISON COMPLETE!")
            print(f"{'='*60}")
            print(f"Open the HTML report to view detailed results:")
            print(f"  {html_file}")
            print(f"{'='*60}\n")

        except Exception as e:
            print(f"\n✗ Error during execution: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()


def main():
    if len(sys.argv) < 4:
        print("Usage: python compare_all_assets.py <email> <password> <site_name>")
        print("Example: python compare_all_assets.py user@example.com mypassword 'Super Caremark'")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    site_name = sys.argv[3]

    comparator = AssetComparator()
    comparator.run(email, password, site_name)


if __name__ == "__main__":
    main()
