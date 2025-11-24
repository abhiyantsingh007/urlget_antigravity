#!/usr/bin/env python3
"""
Extract Asset Names Using JavaScript Execution
This script uses JavaScript to extract data directly from the rendered page
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class JavaScriptAssetExtractor:
    def __init__(self):
        chrome_options = Options()
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

            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)

            sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_button.click()

            time.sleep(8)
            print(f"✓ Login successful!\n")
            return True

        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def navigate_to_assets(self):
        """Navigate to Assets page"""
        print(f"🔍 Navigating to Assets page...")

        try:
            time.sleep(3)

            # Try to find and click Assets link
            try:
                assets_link = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Assets')]"))
                )
                assets_link.click()
                time.sleep(5)
                print(f"✓ Clicked Assets tab\n")
            except:
                # Direct navigation
                current_url = self.driver.current_url
                base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url.split('/site')[0]
                self.driver.get(f"{base_url}/assets")
                time.sleep(5)
                print(f"✓ Navigated via URL\n")

            return True

        except Exception as e:
            print(f"✗ Navigation failed: {str(e)}")
            return False

    def take_debug_screenshot(self, filename):
        """Take screenshot for debugging"""
        self.driver.save_screenshot(filename)
        print(f"📸 Screenshot saved: {filename}")

    def extract_with_javascript(self):
        """Extract asset data using JavaScript"""
        print(f"🔧 Extracting assets using JavaScript...\n")

        # Wait for page to fully load
        time.sleep(5)

        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.take_debug_screenshot(f"assets_page_{timestamp}.png")

        # Try multiple JavaScript extraction strategies

        # Strategy 1: Extract all text content from table cells
        js_script_1 = """
        const cells = document.querySelectorAll('td, [role="cell"]');
        const data = [];
        cells.forEach(cell => {
            const text = cell.innerText || cell.textContent;
            if (text && text.trim()) {
                data.push(text.trim());
            }
        });
        return data;
        """

        # Strategy 2: Look for React component data
        js_script_2 = """
        const rows = document.querySelectorAll('tbody tr, [role="row"]');
        const assets = [];
        rows.forEach(row => {
            const cells = row.querySelectorAll('td, [role="cell"]');
            if (cells.length > 0) {
                const rowData = [];
                cells.forEach(cell => {
                    rowData.push(cell.innerText || cell.textContent || '');
                });
                if (rowData.length > 0 && rowData[0].trim()) {
                    assets.push(rowData);
                }
            }
        });
        return assets;
        """

        # Strategy 3: Get all visible text
        js_script_3 = """
        const bodyText = document.body.innerText;
        return bodyText;
        """

        # Strategy 4: Find MUI DataGrid data
        js_script_4 = """
        // Look for MUI DataGrid
        const dataGrid = document.querySelector('[class*="MuiDataGrid"], [class*="DataGrid"]');
        if (dataGrid) {
            const rows = dataGrid.querySelectorAll('[role="row"]');
            const data = [];
            rows.forEach(row => {
                const cells = row.querySelectorAll('[role="cell"], [role="gridcell"]');
                const rowData = [];
                cells.forEach(cell => {
                    rowData.push(cell.textContent.trim());
                });
                if (rowData.length > 0 && rowData[0]) {
                    data.push(rowData);
                }
            });
            return data;
        }
        return [];
        """

        results = {}

        try:
            print("Strategy 1: Extracting all cell text...")
            result1 = self.driver.execute_script(js_script_1)
            results['all_cells'] = result1
            print(f"  Found {len(result1)} cell texts")
            if result1:
                print(f"  First 10: {result1[:10]}")
        except Exception as e:
            print(f"  Failed: {str(e)}")

        try:
            print("\nStrategy 2: Extracting table rows...")
            result2 = self.driver.execute_script(js_script_2)
            results['table_rows'] = result2
            print(f"  Found {len(result2)} rows")
            if result2:
                print(f"  First row: {result2[0]}")
        except Exception as e:
            print(f"  Failed: {str(e)}")

        try:
            print("\nStrategy 3: Extracting page text...")
            result3 = self.driver.execute_script(js_script_3)
            results['page_text'] = result3
            # Save to file
            with open(f"page_text_{timestamp}.txt", 'w') as f:
                f.write(result3)
            print(f"  Saved page text to: page_text_{timestamp}.txt")
        except Exception as e:
            print(f"  Failed: {str(e)}")

        try:
            print("\nStrategy 4: MUI DataGrid extraction...")
            result4 = self.driver.execute_script(js_script_4)
            results['datagrid_rows'] = result4
            print(f"  Found {len(result4)} DataGrid rows")
            if result4:
                print(f"  First row: {result4[0]}")
        except Exception as e:
            print(f"  Failed: {str(e)}")

        return results

    def parse_asset_names(self, extraction_results):
        """Parse asset names from extraction results"""
        asset_names = []

        # Try to parse from table_rows
        if 'table_rows' in extraction_results and extraction_results['table_rows']:
            print(f"\n📋 Parsing asset names from table rows...")
            for row in extraction_results['table_rows']:
                if len(row) > 0 and row[0]:
                    # First column is usually asset name
                    name = row[0].strip()
                    # Filter out headers and empty values
                    if name and name not in ['Asset Name', 'Name', '', '—']:
                        asset_names.append(name)

        # Try to parse from DataGrid
        if not asset_names and 'datagrid_rows' in extraction_results and extraction_results['datagrid_rows']:
            print(f"\n📋 Parsing asset names from DataGrid...")
            for row in extraction_results['datagrid_rows']:
                if len(row) > 0 and row[0]:
                    name = row[0].strip()
                    if name and name not in ['Asset Name', 'Name', '', '—']:
                        asset_names.append(name)

        # Try to parse from all_cells
        if not asset_names and 'all_cells' in extraction_results:
            print(f"\n📋 Parsing from all cells (looking for patterns)...")
            cells = extraction_results['all_cells']
            # Look for cells that might be asset names
            # Skip common headers and UI elements
            skip_words = ['Asset', 'Name', 'QR', 'Code', 'Condition', 'Class', 'Building',
                         'Actions', 'Rows', 'per', 'page', 'of', '1', '2', '3', '4', '5']
            for cell in cells:
                if cell and len(cell) > 2:  # At least 3 characters
                    if not any(skip in cell for skip in skip_words):
                        if not cell.isdigit():  # Not just a number
                            asset_names.append(cell)

        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in asset_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)

        return unique_names

    def capture_all_assets(self, url, email, password):
        """Capture all assets from a website"""
        print(f"\n{'#'*70}")
        print(f"# CAPTURING ASSETS FROM: {url}")
        print(f"{'#'*70}\n")

        if not self.login(url, email, password):
            return []

        if not self.navigate_to_assets():
            return []

        # Set rows per page to 100
        try:
            print(f"⚙️  Setting rows per page to 100...")
            # Click dropdown
            dropdown = self.driver.find_element(By.XPATH, "//div[contains(@class, 'MuiTablePagination-select')]")
            dropdown.click()
            time.sleep(1)
            # Select 100
            option = self.driver.find_element(By.XPATH, "//li[@data-value='100']")
            option.click()
            time.sleep(3)
            print(f"✓ Set to 100 rows per page\n")
        except:
            print(f"⚠ Could not set rows per page\n")

        # Extract assets using JavaScript
        extraction_results = self.extract_with_javascript()

        # Parse asset names
        asset_names = self.parse_asset_names(extraction_results)

        print(f"\n{'='*70}")
        print(f"✓ Captured {len(asset_names)} asset names")
        print(f"{'='*70}\n")

        if asset_names:
            print("First 10 assets:")
            for i, name in enumerate(asset_names[:10], 1):
                print(f"  {i}. {name}")

        return asset_names

    def close(self):
        """Close browser"""
        try:
            print("\n👋 Closing browser...")
            time.sleep(2)
            self.driver.quit()
        except:
            pass

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 extract_assets_with_javascript.py <email> <password> [site_name]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    site_name = sys.argv[3] if len(sys.argv) > 3 else "Super Caremark"

    rnd_url = "https://acme.egalvanic-rnd.com"
    ai_url = "https://acme.egalvanic.ai"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Capture from RND
    print("\n" + "="*70)
    print("STEP 1: CAPTURING FROM RND")
    print("="*70)

    extractor_rnd = JavaScriptAssetExtractor()
    try:
        rnd_assets = extractor_rnd.capture_all_assets(rnd_url, email, password)

        # Save RND assets
        rnd_file = f"rnd_assets_js_{timestamp}.json"
        with open(rnd_file, 'w') as f:
            json.dump(rnd_assets, f, indent=2)
        print(f"✓ Saved: {rnd_file}")
    finally:
        extractor_rnd.close()

    # Capture from AI
    print("\n" + "="*70)
    print("STEP 2: CAPTURING FROM AI")
    print("="*70)

    extractor_ai = JavaScriptAssetExtractor()
    try:
        ai_assets = extractor_ai.capture_all_assets(ai_url, email, password)

        # Save AI assets
        ai_file = f"ai_assets_js_{timestamp}.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_assets, f, indent=2)
        print(f"✓ Saved: {ai_file}")
    finally:
        extractor_ai.close()

    # Compare
    print("\n" + "="*70)
    print("STEP 3: COMPARING ASSETS")
    print("="*70 + "\n")

    rnd_set = set(rnd_assets)
    ai_set = set(ai_assets)

    missing_from_ai = sorted(list(rnd_set - ai_set))
    new_in_ai = sorted(list(ai_set - rnd_set))
    common = sorted(list(rnd_set & ai_set))

    comparison = {
        'summary': {
            'rnd_total': len(rnd_assets),
            'ai_total': len(ai_assets),
            'difference': len(ai_assets) - len(rnd_assets),
            'common': len(common),
            'missing_from_ai': len(missing_from_ai),
            'new_in_ai': len(new_in_ai)
        },
        'missing_from_ai': missing_from_ai,
        'new_in_ai': new_in_ai,
        'common_assets': common,
        'timestamp': datetime.now().isoformat()
    }

    # Save comparison
    comparison_file = f"asset_comparison_js_{timestamp}.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2)

    # Print results
    print(f"RND Total:           {len(rnd_assets)}")
    print(f"AI Total:            {len(ai_assets)}")
    print(f"Difference:          {len(ai_assets) - len(rnd_assets):+d}")
    print(f"Common:              {len(common)}")
    print(f"Missing from AI:     {len(missing_from_ai)}")
    print(f"New in AI:           {len(new_in_ai)}")
    print("="*70)

    if missing_from_ai:
        print(f"\n🚨 MISSING FROM AI ({len(missing_from_ai)} assets):")
        for asset in missing_from_ai[:20]:
            print(f"  ❌ {asset}")
        if len(missing_from_ai) > 20:
            print(f"  ... and {len(missing_from_ai) - 20} more")

    if new_in_ai:
        print(f"\n➕ NEW IN AI ({len(new_in_ai)} assets):")
        for asset in new_in_ai[:20]:
            print(f"  ✓ {asset}")
        if len(new_in_ai) > 20:
            print(f"  ... and {len(new_in_ai) - 20} more")

    print(f"\n✓ Comparison saved: {comparison_file}\n")

if __name__ == "__main__":
    main()
