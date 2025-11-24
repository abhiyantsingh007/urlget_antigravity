#!/usr/bin/env python3
"""
Asset Names Comparison - Captures actual asset names and identifies missing ones
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AssetNameComparator:
    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, url, email, password):
        """Login to the website"""
        print(f"\n{'='*70}")
        print(f"🔐 Logging into: {url}")
        print(f"{'='*70}")

        self.driver.get(f"{url}/login")
        time.sleep(3)

        try:
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            print(f"✓ Entered email")

            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            print(f"✓ Entered password")

            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()
            print(f"✓ Clicked Sign In")

            time.sleep(8)

            current_url = self.driver.current_url
            if "dashboard" in current_url or "site" in current_url:
                print(f"✓ Login successful!\n")
                return True
            else:
                print(f"⚠ Unexpected URL after login: {current_url}")
                return False

        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def navigate_to_assets(self):
        """Navigate to Assets page by clicking the Assets tab"""
        print(f"🔍 Navigating to Assets page...")

        try:
            # Wait a moment for dashboard to fully load
            time.sleep(3)

            # Try multiple selectors for Assets link
            selectors = [
                "//a[contains(text(), 'Assets')]",
                "//a[contains(@href, '/assets')]",
                "//button[contains(text(), 'Assets')]",
                "//*[contains(text(), 'Assets') and (self::a or self::button)]"
            ]

            for selector in selectors:
                try:
                    assets_link = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    assets_link.click()
                    time.sleep(4)
                    print(f"✓ Clicked Assets tab")
                    return True
                except:
                    continue

            # If clicking didn't work, try direct URL navigation
            print(f"⚠ Could not click Assets link, trying direct navigation...")
            current_url = self.driver.current_url
            base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url.split('/site')[0]
            self.driver.get(f"{base_url}/assets")
            time.sleep(4)
            print(f"✓ Navigated to Assets page via URL")
            return True

        except Exception as e:
            print(f"✗ Could not navigate to Assets: {str(e)}")
            return False

    def get_total_assets_count(self):
        """Get total asset count from pagination"""
        try:
            time.sleep(2)
            # Look for pagination text like "1-25 of 179"
            pagination_elements = self.driver.find_elements(By.XPATH,
                "//*[contains(text(), 'of') and contains(text(), '–')]")

            for elem in pagination_elements:
                text = elem.text.strip()
                if '–' in text and 'of' in text:
                    total = text.split('of')[-1].strip()
                    return int(total)
        except:
            pass
        return 0

    def set_rows_per_page(self, rows=100):
        """Set rows per page to maximum"""
        try:
            print(f"⚙️  Setting rows per page to {rows}...")

            # Click on rows per page dropdown
            selectors = [
                "//div[contains(@class, 'MuiTablePagination-select')]",
                "select[name='rowsPerPage']",
                "//*[contains(@aria-label, 'rows per page')]"
            ]

            for selector in selectors:
                try:
                    dropdown = self.driver.find_element(By.XPATH, selector)
                    dropdown.click()
                    time.sleep(1)

                    # Select 100 option
                    option = self.driver.find_element(By.XPATH, f"//li[@data-value='{rows}' or contains(text(), '{rows}')]")
                    option.click()
                    time.sleep(2)
                    print(f"✓ Set to {rows} rows per page\n")
                    return True
                except:
                    continue

        except Exception as e:
            print(f"⚠ Could not set rows per page: {str(e)}\n")

        return False

    def extract_asset_names_from_page(self):
        """Extract asset names from current page"""
        asset_names = []

        try:
            time.sleep(2)

            # Strategy 1: Look for table cells in first column
            # First column typically contains asset names
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            print(f"  Found {len(table_rows)} table rows")

            for row in table_rows:
                try:
                    # Get first cell (asset name is usually first)
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        asset_name = cells[0].text.strip()
                        if asset_name and asset_name not in ['', '—', 'Asset Name']:
                            asset_names.append(asset_name)
                except:
                    continue

            # Strategy 2: If no names found, try finding all cells and look for asset patterns
            if not asset_names:
                print(f"  Trying alternative method...")
                all_cells = self.driver.find_elements(By.XPATH, "//tbody//td")

                # Asset names are typically in groups - extract every 5th or 6th element
                # or look for cells that contain text matching asset name patterns
                for i, cell in enumerate(all_cells):
                    text = cell.text.strip()
                    if text and text not in ['', '—', '1', '2', '3', '4', '5']:
                        # Check if it looks like an asset name (not a number, not a dash)
                        if not text.replace('.', '').replace('-', '').isdigit():
                            if len(text) > 1:  # More than 1 character
                                asset_names.append(text)

                # Remove duplicates while preserving order
                asset_names = list(dict.fromkeys(asset_names))

        except Exception as e:
            print(f"  ⚠ Error extracting names: {str(e)}")

        return asset_names

    def click_next_page(self):
        """Click next page button"""
        try:
            # Look for next button
            next_button = self.driver.find_element(By.XPATH,
                "//button[@aria-label='Go to next page' or @aria-label='Next page']")

            if next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class').lower():
                next_button.click()
                time.sleep(3)
                return True

        except:
            pass

        return False

    def capture_all_asset_names(self, url, email, password, site_name):
        """Capture all asset names from a website"""
        print(f"\n{'#'*70}")
        print(f"# Capturing Asset Names from: {url}")
        print(f"# Site: {site_name}")
        print(f"{'#'*70}\n")

        if not self.login(url, email, password):
            return []

        if not self.navigate_to_assets():
            return []

        # Get total count
        total_count = self.get_total_assets_count()
        print(f"📊 Total assets detected: {total_count}\n")

        # Set rows per page to maximum
        self.set_rows_per_page(100)

        all_asset_names = []
        page_num = 1
        max_pages = 10  # Safety limit

        while page_num <= max_pages:
            print(f"📄 Page {page_num}:")

            # Extract names from current page
            page_names = self.extract_asset_names_from_page()

            if page_names:
                # Filter out common table headers and noise
                filtered_names = [name for name in page_names
                                 if name not in ['Asset Name', 'QR Code', 'Condition',
                                               'Asset Class', 'Building', 'Actions']]

                new_names = [name for name in filtered_names if name not in all_asset_names]
                all_asset_names.extend(new_names)

                print(f"  ✓ Extracted {len(new_names)} new asset names")
                print(f"  Total captured so far: {len(all_asset_names)}")

                # Show first 3 names from this page
                if new_names:
                    print(f"  Sample: {', '.join(new_names[:3])}")
            else:
                print(f"  ⚠ No new names extracted from page {page_num}")

            # Check if we have all assets
            if total_count > 0 and len(all_asset_names) >= total_count:
                print(f"\n✓ Captured all {len(all_asset_names)} asset names!")
                break

            # Try to go to next page
            if not self.click_next_page():
                print(f"\n✓ No more pages. Captured {len(all_asset_names)} asset names total.")
                break

            page_num += 1

        print(f"\n{'='*70}")
        print(f"✓ Captured {len(all_asset_names)} total asset names")
        print(f"{'='*70}\n")

        return all_asset_names

    def compare_asset_names(self, rnd_names, ai_names):
        """Compare asset name lists and identify differences"""
        print(f"\n{'='*70}")
        print(f"📊 COMPARING ASSET NAMES")
        print(f"{'='*70}\n")

        # Convert to sets for comparison
        rnd_set = set(rnd_names)
        ai_set = set(ai_names)

        # Find differences
        only_in_rnd = sorted(list(rnd_set - ai_set))
        only_in_ai = sorted(list(ai_set - rnd_set))
        common = sorted(list(rnd_set & ai_set))

        comparison = {
            'summary': {
                'rnd_total': len(rnd_names),
                'ai_total': len(ai_names),
                'difference': len(ai_names) - len(rnd_names),
                'common_assets': len(common),
                'missing_from_ai': len(only_in_rnd),
                'new_in_ai': len(only_in_ai)
            },
            'assets_missing_from_ai': only_in_rnd,
            'assets_new_in_ai': only_in_ai,
            'common_assets': common,
            'timestamp': datetime.now().isoformat()
        }

        return comparison

    def generate_html_report(self, comparison, output_file):
        """Generate detailed HTML report with asset names"""

        summary = comparison['summary']
        missing_from_ai = comparison['assets_missing_from_ai']
        new_in_ai = comparison['assets_new_in_ai']

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Asset Names Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 36px; }}
        .summary {{ background: white; padding: 30px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 25px 0; }}
        .stat {{ background: #f8f9fa; padding: 25px; border-radius: 10px; text-align: center; border-left: 5px solid; }}
        .stat-number {{ font-size: 48px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #6c757d; font-size: 14px; text-transform: uppercase; }}
        .critical {{ border-color: #dc3545; }} .critical .stat-number {{ color: #dc3545; }}
        .warning {{ border-color: #fd7e14; }} .warning .stat-number {{ color: #fd7e14; }}
        .success {{ border-color: #28a745; }} .success .stat-number {{ color: #28a745; }}
        .info {{ border-color: #0dcaf0; }} .info .stat-number {{ color: #0dcaf0; }}
        .section {{ background: white; padding: 30px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .alert {{ padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 6px solid; }}
        .alert-critical {{ background: #f8d7da; border-left-color: #dc3545; }}
        .alert-warning {{ background: #fff3cd; border-left-color: #ffc107; }}
        .alert-success {{ background: #d1f2eb; border-left-color: #28a745; }}
        .asset-list {{ columns: 3; column-gap: 20px; margin: 20px 0; }}
        .asset-item {{ break-inside: avoid; padding: 8px 12px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; border-left: 3px solid #0dcaf0; }}
        .asset-item-missing {{ border-left-color: #dc3545; background: #f8d7da; }}
        .asset-item-new {{ border-left-color: #28a745; background: #d1f2eb; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Asset Names Comparison Report</h1>
        <p>Detailed comparison of actual asset names between RND and AI environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>📊 Summary Statistics</h2>
        <div class="stats">
            <div class="stat info">
                <div class="stat-number">{summary['rnd_total']}</div>
                <div class="stat-label">RND Assets</div>
            </div>
            <div class="stat info">
                <div class="stat-number">{summary['ai_total']}</div>
                <div class="stat-label">AI Assets</div>
            </div>
            <div class="stat {'warning' if summary['difference'] != 0 else 'success'}">
                <div class="stat-number">{summary['difference']:+d}</div>
                <div class="stat-label">Difference</div>
            </div>
            <div class="stat success">
                <div class="stat-number">{summary['common_assets']}</div>
                <div class="stat-label">Common Assets</div>
            </div>
            <div class="stat {'critical' if summary['missing_from_ai'] > 0 else 'success'}">
                <div class="stat-number">{summary['missing_from_ai']}</div>
                <div class="stat-label">Missing from AI</div>
            </div>
            <div class="stat {'warning' if summary['new_in_ai'] > 0 else 'success'}">
                <div class="stat-number">{summary['new_in_ai']}</div>
                <div class="stat-label">New in AI</div>
            </div>
        </div>
    </div>
"""

        # Missing from AI section
        if missing_from_ai:
            html += f"""
    <div class="section">
        <h2>🚨 Assets Missing from AI ({len(missing_from_ai)})</h2>
        <div class="alert alert-critical">
            <strong>⚠️ CRITICAL:</strong> The following assets exist in RND but are MISSING from the AI environment.
            These assets were not migrated or were lost during migration.
        </div>
        <div class="asset-list">
"""
            for i, asset_name in enumerate(missing_from_ai, 1):
                html += f'            <div class="asset-item asset-item-missing"><strong>{i}.</strong> {asset_name}</div>\n'

            html += """        </div>
    </div>
"""
        else:
            html += """
    <div class="section">
        <h2>✅ No Assets Missing from AI</h2>
        <div class="alert alert-success">
            All RND assets have been successfully migrated to the AI environment.
        </div>
    </div>
"""

        # New in AI section
        if new_in_ai:
            html += f"""
    <div class="section">
        <h2>➕ New Assets in AI ({len(new_in_ai)})</h2>
        <div class="alert alert-warning">
            <strong>ℹ️ For Review:</strong> The following assets exist in AI but NOT in RND.
            These could be newly added assets or indicate naming discrepancies.
        </div>
        <div class="asset-list">
"""
            for i, asset_name in enumerate(new_in_ai, 1):
                html += f'            <div class="asset-item asset-item-new"><strong>{i}.</strong> {asset_name}</div>\n'

            html += """        </div>
    </div>
"""
        else:
            html += """
    <div class="section">
        <h2>✅ No New Assets in AI</h2>
        <div class="alert alert-success">
            The AI environment contains no additional assets beyond RND.
        </div>
    </div>
"""

        html += """
    <div style="text-align: center; padding: 20px; color: #6c757d; font-size: 12px;">
        <p>Asset Names Comparison Report</p>
        <p>Generated by Asset Migration Verification System</p>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✓ HTML report generated: {output_file}")

    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
        except:
            pass

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 capture_asset_names_comparison.py <email> <password> [site_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    site_name = sys.argv[3] if len(sys.argv) > 3 else "Super Caremark"

    rnd_url = "https://acme.egalvanic-rnd.com"
    ai_url = "https://acme.egalvanic.ai"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    comparator = AssetNameComparator(headless=False)

    try:
        # Capture from RND
        print("\n" + "="*70)
        print("STEP 1: Capturing asset names from RND website")
        print("="*70)
        rnd_asset_names = comparator.capture_all_asset_names(rnd_url, email, password, site_name)

        # Save RND names
        rnd_file = f"rnd_asset_names_{timestamp}.json"
        with open(rnd_file, 'w') as f:
            json.dump(rnd_asset_names, f, indent=2)
        print(f"✓ Saved RND asset names: {rnd_file}")

        # Capture from AI
        print("\n" + "="*70)
        print("STEP 2: Capturing asset names from AI website")
        print("="*70)
        ai_asset_names = comparator.capture_all_asset_names(ai_url, email, password, site_name)

        # Save AI names
        ai_file = f"ai_asset_names_{timestamp}.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_asset_names, f, indent=2)
        print(f"✓ Saved AI asset names: {ai_file}")

        # Compare
        print("\n" + "="*70)
        print("STEP 3: Comparing asset names")
        print("="*70)
        comparison = comparator.compare_asset_names(rnd_asset_names, ai_asset_names)

        # Save comparison
        comparison_file = f"asset_names_comparison_{timestamp}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"✓ Saved comparison: {comparison_file}")

        # Generate HTML report
        report_file = f"ASSET_NAMES_REPORT_{timestamp}.html"
        comparator.generate_html_report(comparison, report_file)

        # Print summary
        print("\n" + "="*70)
        print("FINAL SUMMARY")
        print("="*70)
        print(f"RND Assets:             {comparison['summary']['rnd_total']}")
        print(f"AI Assets:              {comparison['summary']['ai_total']}")
        print(f"Difference:             {comparison['summary']['difference']:+d}")
        print(f"Common Assets:          {comparison['summary']['common_assets']}")
        print(f"Missing from AI:        {comparison['summary']['missing_from_ai']}")
        print(f"New in AI:              {comparison['summary']['new_in_ai']}")
        print("="*70)

        if comparison['assets_missing_from_ai']:
            print("\n🚨 ASSETS MISSING FROM AI:")
            for asset in comparison['assets_missing_from_ai'][:10]:
                print(f"  ❌ {asset}")
            if len(comparison['assets_missing_from_ai']) > 10:
                print(f"  ... and {len(comparison['assets_missing_from_ai']) - 10} more")

        if comparison['assets_new_in_ai']:
            print("\n➕ NEW ASSETS IN AI:")
            for asset in comparison['assets_new_in_ai'][:10]:
                print(f"  ✓ {asset}")
            if len(comparison['assets_new_in_ai']) > 10:
                print(f"  ... and {len(comparison['assets_new_in_ai']) - 10} more")

        print(f"\n✓ Open the HTML report for full details: {report_file}")
        print("="*70 + "\n")

    finally:
        comparator.close()

if __name__ == "__main__":
    main()
