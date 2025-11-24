#!/usr/bin/env python3
"""
Complete Asset Capture with Pagination
Captures ALL assets from both RND and AI websites and identifies missing assets
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class AssetComparator:
    def __init__(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)

    def login(self, url, email, password):
        """Login to the website"""
        print(f"\n{'='*60}")
        print(f"Logging into: {url}")
        print(f"{'='*60}")

        self.driver.get(f"{url}/login")
        time.sleep(3)

        try:
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(email)
            print(f"✓ Entered email: {email}")

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
                print(f"✓ Login successful!")
                return True
            else:
                print(f"⚠ Unexpected URL after login: {current_url}")
                return False

        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def navigate_to_assets(self):
        """Navigate to assets page"""
        print(f"\n🔍 Navigating to Assets page...")
        try:
            # Try to find and click Assets link
            assets_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/assets') or contains(text(), 'Assets')]"))
            )
            assets_link.click()
            time.sleep(3)
            print(f"✓ Navigated to Assets page")
            return True
        except Exception as e:
            # Try direct navigation
            print(f"⚠ Could not click Assets link, trying direct navigation...")
            current_url = self.driver.current_url
            base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url
            self.driver.get(f"{base_url}/assets")
            time.sleep(3)
            print(f"✓ Navigated to Assets page via URL")
            return True

    def extract_assets_from_table(self):
        """Extract assets from current page using multiple strategies"""
        assets = []

        try:
            # Wait for table to load
            time.sleep(2)

            # Strategy 1: Look for table rows with data-id or role="row"
            rows = self.driver.find_elements(By.CSS_SELECTOR,
                "tr[data-id], tbody tr, tr[role='row'], .MuiTableRow-root")

            print(f"  Found {len(rows)} potential row elements")

            for row in rows:
                try:
                    # Skip header rows
                    if 'header' in row.get_attribute('class').lower():
                        continue

                    # Get all cells in the row
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) >= 5:  # Should have at least 5 columns
                        asset = {
                            'name': cells[0].text.strip(),
                            'qr_code': cells[1].text.strip(),
                            'condition': cells[2].text.strip(),
                            'asset_class': cells[3].text.strip(),
                            'building': cells[4].text.strip()
                        }

                        # Only add if name is not empty
                        if asset['name'] and asset['name'] != '—':
                            assets.append(asset)

                except Exception as e:
                    continue

            # Strategy 2: If no assets found, try alternative selectors
            if not assets:
                print(f"  Trying alternative extraction method...")
                # Look for divs with asset data
                asset_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    "[data-field='name'], [data-field='assetName']")

                for elem in asset_elements:
                    try:
                        name = elem.text.strip()
                        if name and name != '—':
                            # Try to get parent row
                            parent = elem.find_element(By.XPATH, "./ancestor::tr")
                            cells = parent.find_elements(By.TAG_NAME, "td")

                            if len(cells) >= 4:
                                asset = {
                                    'name': name,
                                    'qr_code': cells[1].text.strip() if len(cells) > 1 else '—',
                                    'condition': cells[2].text.strip() if len(cells) > 2 else '—',
                                    'asset_class': cells[3].text.strip() if len(cells) > 3 else '—',
                                    'building': cells[4].text.strip() if len(cells) > 4 else '—'
                                }
                                assets.append(asset)
                    except:
                        continue

        except Exception as e:
            print(f"  ⚠ Error extracting assets: {str(e)}")

        return assets

    def set_rows_per_page(self, count=100):
        """Set rows per page to maximum"""
        try:
            print(f"\n⚙ Setting rows per page to {count}...")

            # Look for rows per page dropdown
            selectors = [
                "select[name='rowsPerPage']",
                "[aria-label*='Rows per page'] select",
                "[aria-label*='rows per page']",
                ".MuiTablePagination-select",
                "select"
            ]

            for selector in selectors:
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, selector)
                    dropdown.click()
                    time.sleep(1)

                    # Try to select 100
                    options = self.driver.find_elements(By.CSS_SELECTOR, "option, li[role='option']")
                    for option in options:
                        if '100' in option.text:
                            option.click()
                            time.sleep(2)
                            print(f"✓ Set to {count} rows per page")
                            return True
                    break
                except:
                    continue

            print(f"⚠ Could not set rows per page, using default")
            return False

        except Exception as e:
            print(f"⚠ Error setting rows per page: {str(e)}")
            return False

    def get_total_asset_count(self):
        """Get total number of assets from pagination text"""
        try:
            # Look for text like "1-25 of 179"
            pagination_texts = self.driver.find_elements(By.XPATH,
                "//*[contains(text(), 'of') and contains(text(), '–')]")

            for elem in pagination_texts:
                text = elem.text.strip()
                if '–' in text and 'of' in text:
                    # Extract total from "1–25 of 179"
                    total = text.split('of')[-1].strip()
                    return int(total)

        except:
            pass

        return 0

    def click_next_page(self):
        """Click next page button"""
        try:
            # Look for next button
            next_selectors = [
                "button[aria-label='Go to next page']",
                "button[aria-label='Next page']",
                ".MuiTablePagination-actions button:last-child",
                "button[title*='Next']"
            ]

            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class'):
                        next_button.click()
                        time.sleep(3)
                        return True
                except:
                    continue

            return False

        except Exception as e:
            return False

    def capture_all_assets(self, url, email, password, site_name="Super Caremark"):
        """Capture all assets with pagination"""
        print(f"\n{'#'*60}")
        print(f"# Capturing assets from: {url}")
        print(f"# Site: {site_name}")
        print(f"{'#'*60}")

        if not self.login(url, email, password):
            return []

        if not self.navigate_to_assets():
            return []

        # Get total count
        total_count = self.get_total_asset_count()
        print(f"\n✓ Total assets available: {total_count}")

        # Set rows per page to 100
        self.set_rows_per_page(100)

        all_assets = []
        page_num = 1

        while True:
            print(f"\n📄 Processing page {page_num}...")

            # Extract assets from current page
            page_assets = self.extract_assets_from_table()

            if page_assets:
                print(f"  ✓ Extracted {len(page_assets)} assets from page {page_num}")
                all_assets.extend(page_assets)
            else:
                print(f"  ⚠ No assets extracted from page {page_num}")

            print(f"  Total assets captured so far: {len(all_assets)}")

            # Check if we have all assets
            if total_count > 0 and len(all_assets) >= total_count:
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

    def compare_assets(self, rnd_assets, ai_assets):
        """Compare asset lists and identify differences"""
        print(f"\n{'='*60}")
        print(f"📊 ASSET COMPARISON ANALYSIS")
        print(f"{'='*60}")

        # Create dictionaries for easy lookup
        rnd_dict = {asset['name']: asset for asset in rnd_assets}
        ai_dict = {asset['name']: asset for asset in ai_assets}

        # Find differences
        only_in_rnd = [name for name in rnd_dict if name not in ai_dict]
        only_in_ai = [name for name in ai_dict if name not in rnd_dict]
        common = [name for name in rnd_dict if name in ai_dict]

        # Find field differences in common assets
        field_diffs = []
        for name in common:
            rnd_asset = rnd_dict[name]
            ai_asset = ai_dict[name]

            diffs = {}
            for field in ['qr_code', 'condition', 'asset_class', 'building']:
                if rnd_asset.get(field) != ai_asset.get(field):
                    diffs[field] = {
                        'rnd': rnd_asset.get(field),
                        'ai': ai_asset.get(field)
                    }

            if diffs:
                field_diffs.append({
                    'asset_name': name,
                    'differences': diffs
                })

        comparison = {
            'summary': {
                'rnd_total': len(rnd_assets),
                'ai_total': len(ai_assets),
                'difference': len(ai_assets) - len(rnd_assets),
                'common_assets': len(common),
                'only_in_rnd': len(only_in_rnd),
                'only_in_ai': len(only_in_ai),
                'field_differences': len(field_diffs)
            },
            'missing_from_ai': only_in_rnd,
            'missing_from_rnd': only_in_ai,
            'field_differences': field_diffs,
            'timestamp': datetime.now().isoformat()
        }

        return comparison

    def generate_detailed_report(self, comparison, output_file):
        """Generate detailed HTML report with missing assets"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Detailed Asset Comparison - Missing Assets Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #6c757d; font-size: 14px; }}
        .critical {{ border-color: #dc3545; }} .critical .stat-number {{ color: #dc3545; }}
        .warning {{ border-color: #fd7e14; }} .warning .stat-number {{ color: #fd7e14; }}
        .success {{ border-color: #28a745; }} .success .stat-number {{ color: #28a745; }}
        .info {{ border-color: #0dcaf0; }} .info .stat-number {{ color: #0dcaf0; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
        .badge-danger {{ background: #f8d7da; color: #dc3545; }}
        .badge-warning {{ background: #fff3cd; color: #fd7e14; }}
        .badge-success {{ background: #d1f2eb; color: #28a745; }}
        .alert {{ padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid; }}
        .alert-danger {{ background: #f8d7da; border-left-color: #dc3545; color: #721c24; }}
        .alert-warning {{ background: #fff3cd; border-left-color: #ffc107; color: #856404; }}
        .alert-info {{ background: #cfe2ff; border-left-color: #0dcaf0; color: #055160; }}
        .asset-list {{ columns: 3; column-gap: 20px; }}
        .asset-item {{ break-inside: avoid; padding: 8px 0; border-bottom: 1px solid #dee2e6; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
        .diff-table {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }}
        .diff-cell {{ padding: 10px; background: #f8f9fa; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Detailed Asset Comparison Report</h1>
        <p>Complete analysis of assets between RND and AI environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>📊 Summary Statistics</h2>
        <div class="stats">
            <div class="stat info">
                <div class="stat-number">{comparison['summary']['rnd_total']}</div>
                <div class="stat-label">RND Assets</div>
            </div>
            <div class="stat info">
                <div class="stat-number">{comparison['summary']['ai_total']}</div>
                <div class="stat-label">AI Assets</div>
            </div>
            <div class="stat {'warning' if comparison['summary']['difference'] != 0 else 'success'}">
                <div class="stat-number">{comparison['summary']['difference']:+d}</div>
                <div class="stat-label">Difference</div>
            </div>
            <div class="stat success">
                <div class="stat-number">{comparison['summary']['common_assets']}</div>
                <div class="stat-label">Common Assets</div>
            </div>
            <div class="stat {'critical' if comparison['summary']['only_in_rnd'] > 0 else 'success'}">
                <div class="stat-number">{comparison['summary']['only_in_rnd']}</div>
                <div class="stat-label">Missing from AI</div>
            </div>
            <div class="stat {'warning' if comparison['summary']['only_in_ai'] > 0 else 'success'}">
                <div class="stat-number">{comparison['summary']['only_in_ai']}</div>
                <div class="stat-label">New in AI</div>
            </div>
            <div class="stat {'warning' if comparison['summary']['field_differences'] > 0 else 'success'}">
                <div class="stat-number">{comparison['summary']['field_differences']}</div>
                <div class="stat-label">Field Differences</div>
            </div>
        </div>
    </div>
"""

        # Missing from AI (Critical)
        if comparison['missing_from_ai']:
            html += f"""
    <div class="section">
        <h2>🚨 CRITICAL: Assets Missing from AI ({len(comparison['missing_from_ai'])})</h2>
        <div class="alert alert-danger">
            <strong>⚠️ Action Required:</strong> These assets exist in RND but are MISSING from the AI environment.
            This indicates potential data migration issues that need immediate attention.
        </div>
        <div class="asset-list">
"""
            for i, asset_name in enumerate(sorted(comparison['missing_from_ai']), 1):
                html += f'            <div class="asset-item"><strong>{i}.</strong> {asset_name}</div>\n'

            html += """        </div>
    </div>
"""
        else:
            html += """
    <div class="section">
        <h2>✅ No Assets Missing from AI</h2>
        <div class="alert alert-info">
            All RND assets have been successfully migrated to the AI environment.
        </div>
    </div>
"""

        # New in AI (Warning)
        if comparison['missing_from_rnd']:
            html += f"""
    <div class="section">
        <h2>⚠️ New Assets in AI ({len(comparison['missing_from_rnd'])})</h2>
        <div class="alert alert-warning">
            <strong>ℹ️ For Review:</strong> These assets exist in AI but NOT in RND.
            These could be newly added assets or indicate naming discrepancies.
        </div>
        <div class="asset-list">
"""
            for i, asset_name in enumerate(sorted(comparison['missing_from_rnd']), 1):
                html += f'            <div class="asset-item"><strong>{i}.</strong> {asset_name}</div>\n'

            html += """        </div>
    </div>
"""
        else:
            html += """
    <div class="section">
        <h2>✅ No New Assets in AI</h2>
        <div class="alert alert-info">
            The AI environment contains no additional assets beyond RND.
        </div>
    </div>
"""

        # Field Differences
        if comparison['field_differences']:
            html += f"""
    <div class="section">
        <h2>📝 Assets with Field Differences ({len(comparison['field_differences'])})</h2>
        <div class="alert alert-warning">
            These assets exist in both environments but have different field values.
        </div>

        <table>
            <thead>
                <tr>
                    <th>Asset Name</th>
                    <th>Field</th>
                    <th>RND Value</th>
                    <th>AI Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""
            for item in comparison['field_differences']:
                for field, values in item['differences'].items():
                    rnd_val = values['rnd'] if values['rnd'] else '—'
                    ai_val = values['ai'] if values['ai'] else '—'
                    html += f"""                <tr>
                    <td><strong>{item['asset_name']}</strong></td>
                    <td><code>{field}</code></td>
                    <td>{rnd_val}</td>
                    <td>{ai_val}</td>
                    <td><span class="badge badge-warning">Different</span></td>
                </tr>
"""

            html += """            </tbody>
        </table>
    </div>
"""

        # Recommendations
        html += """
    <div class="section">
        <h2>💡 Recommendations</h2>
        <ol>
"""

        if comparison['missing_from_ai']:
            html += f"""            <li><strong>CRITICAL Priority:</strong> Investigate why {len(comparison['missing_from_ai'])} assets are missing from AI.
                Verify if they should be migrated or if they were intentionally excluded.</li>
"""

        if comparison['missing_from_rnd']:
            html += f"""            <li><strong>HIGH Priority:</strong> Review the {len(comparison['missing_from_rnd'])} new assets in AI.
                Verify if they are legitimate additions or if there are naming/identification issues.</li>
"""

        if comparison['field_differences']:
            html += f"""            <li><strong>MEDIUM Priority:</strong> Review {len(comparison['field_differences'])} assets with field differences.
                Ensure data consistency between environments.</li>
"""

        if not (comparison['missing_from_ai'] or comparison['missing_from_rnd'] or comparison['field_differences']):
            html += """            <li><strong>✅ Excellent:</strong> All assets match perfectly between RND and AI environments.
                No action required.</li>
"""

        html += """        </ol>
    </div>

    <div style="text-align: center; padding: 20px; color: #6c757d; font-size: 12px;">
        <p>Asset Comparison Report - For Internal Use</p>
        <p>Report generated by automated asset comparison tool</p>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"\n✓ Detailed HTML report generated: {output_file}")

    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
        except:
            pass

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 capture_all_assets_with_pagination.py <email> <password> [site_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    site_name = sys.argv[3] if len(sys.argv) > 3 else "Super Caremark"

    rnd_url = "https://acme.egalvanic-rnd.com"
    ai_url = "https://acme.egalvanic.ai"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    comparator = AssetComparator(headless=False)

    try:
        # Capture from RND
        print("\n" + "="*60)
        print("STEP 1: Capturing assets from RND website")
        print("="*60)
        rnd_assets = comparator.capture_all_assets(rnd_url, email, password, site_name)

        # Save RND assets
        rnd_file = f"rnd_complete_assets_{timestamp}.json"
        with open(rnd_file, 'w') as f:
            json.dump(rnd_assets, f, indent=2)
        print(f"\n✓ Saved RND assets: {rnd_file}")

        # Capture from AI
        print("\n" + "="*60)
        print("STEP 2: Capturing assets from AI website")
        print("="*60)
        ai_assets = comparator.capture_all_assets(ai_url, email, password, site_name)

        # Save AI assets
        ai_file = f"ai_complete_assets_{timestamp}.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_assets, f, indent=2)
        print(f"\n✓ Saved AI assets: {ai_file}")

        # Compare
        print("\n" + "="*60)
        print("STEP 3: Comparing assets")
        print("="*60)
        comparison = comparator.compare_assets(rnd_assets, ai_assets)

        # Save comparison
        comparison_file = f"detailed_asset_comparison_{timestamp}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"✓ Saved comparison: {comparison_file}")

        # Generate HTML report
        report_file = f"MISSING_ASSETS_REPORT_{timestamp}.html"
        comparator.generate_detailed_report(comparison, report_file)

        # Print summary
        print("\n" + "="*60)
        print("COMPARISON SUMMARY")
        print("="*60)
        print(f"RND Total:              {comparison['summary']['rnd_total']}")
        print(f"AI Total:               {comparison['summary']['ai_total']}")
        print(f"Difference:             {comparison['summary']['difference']:+d}")
        print(f"Common Assets:          {comparison['summary']['common_assets']}")
        print(f"Missing from AI:        {comparison['summary']['only_in_rnd']}")
        print(f"New in AI:              {comparison['summary']['only_in_ai']}")
        print(f"Field Differences:      {comparison['summary']['field_differences']}")
        print("="*60)

        if comparison['missing_from_ai']:
            print("\n🚨 CRITICAL: The following assets are MISSING from AI:")
            for asset in sorted(comparison['missing_from_ai'])[:10]:
                print(f"  - {asset}")
            if len(comparison['missing_from_ai']) > 10:
                print(f"  ... and {len(comparison['missing_from_ai']) - 10} more")

        if comparison['missing_from_rnd']:
            print("\n⚠️  WARNING: The following assets are NEW in AI:")
            for asset in sorted(comparison['missing_from_rnd'])[:10]:
                print(f"  - {asset}")
            if len(comparison['missing_from_rnd']) > 10:
                print(f"  ... and {len(comparison['missing_from_rnd']) - 10} more")

        print(f"\n✓ Open the HTML report for full details: {report_file}")
        print("="*60)

    finally:
        comparator.close()

if __name__ == "__main__":
    main()
