#!/usr/bin/env python3
"""
FINAL Complete Asset Capture - Gets ALL asset names with pagination and scrolling
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class CompleteAssetCapture:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, url, email, password):
        """Login"""
        print(f"\n{'='*70}")
        print(f"🔐 Logging into: {url}")
        print(f"{'='*70}")

        self.driver.get(f"{url}/login")
        time.sleep(3)

        email_field = self.wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(email)

        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys(password)

        sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        sign_in_button.click()
        time.sleep(8)

        print(f"✓ Login successful!\n")
        return True

    def navigate_to_assets(self):
        """Navigate to Assets"""
        print(f"🔍 Navigating to Assets...")
        time.sleep(3)

        try:
            assets_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Assets')]")))
            assets_link.click()
        except:
            current_url = self.driver.current_url
            base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url.split('/site')[0]
            self.driver.get(f"{base_url}/assets")

        time.sleep(5)
        print(f"✓ On Assets page\n")
        return True

    def set_rows_100(self):
        """Set rows per page to 100"""
        print(f"⚙️  Setting rows per page to 100...")
        try:
            dropdown = self.driver.find_element(By.XPATH, "//div[contains(@class, 'MuiTablePagination-select')]")
            dropdown.click()
            time.sleep(1)
            option = self.driver.find_element(By.XPATH, "//li[@data-value='100']")
            option.click()
            time.sleep(5)  # Wait longer for table to reload
            print(f"✓ Set to 100 rows\n")
            return True
        except:
            print(f"⚠ Could not set rows\n")
            return False

    def scroll_page(self):
        """Scroll to load all content"""
        print(f"📜 Scrolling page to load all data...")
        # Scroll down
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        # Scroll up
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        # Scroll middle
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        print(f"✓ Scrolling complete\n")

    def extract_assets_from_page(self):
        """Extract all asset names from current page using JavaScript"""
        print(f"🔧 Extracting assets from current page...")

        # Scroll first to ensure all data is loaded
        self.scroll_page()

        # JavaScript to extract from MUI DataGrid
        js_script = """
        const rows = document.querySelectorAll('[role="row"]');
        const assets = [];
        rows.forEach(row => {
            const cells = row.querySelectorAll('[role="cell"], [role="gridcell"]');
            if (cells.length > 0) {
                const firstCell = cells[0].textContent.trim();
                if (firstCell &&
                    firstCell !== 'Asset Name' &&
                    firstCell !== 'Name' &&
                    firstCell !== '' &&
                    firstCell.length > 1) {
                    assets.push(firstCell);
                }
            }
        });
        return assets;
        """

        try:
            assets = self.driver.execute_script(js_script)
            print(f"  ✓ Found {len(assets)} assets on this page")
            if assets:
                print(f"  First few: {assets[:5]}")
            return assets
        except Exception as e:
            print(f"  ⚠ Extraction failed: {str(e)}")
            return []

    def click_next_page(self):
        """Click next page button"""
        try:
            next_button = self.driver.find_element(By.XPATH,
                "//button[@aria-label='Go to next page' or contains(@aria-label, 'Next')]")

            if next_button.is_enabled() and 'disabled' not in next_button.get_attribute('class').lower():
                next_button.click()
                time.sleep(4)  # Wait for page to load
                return True
        except:
            pass
        return False

    def capture_all_assets(self, url, email, password):
        """Capture ALL assets with pagination"""
        print(f"\n{'#'*70}")
        print(f"# CAPTURING ALL ASSETS FROM: {url}")
        print(f"{'#'*70}\n")

        if not self.login(url, email, password):
            return []

        if not self.navigate_to_assets():
            return []

        # Set to 100 rows per page
        self.set_rows_100()

        all_assets = []
        page_num = 1
        max_pages = 5  # Safety limit (100 rows * 5 pages = 500 assets max)

        while page_num <= max_pages:
            print(f"\n📄 Page {page_num}:")

            # Extract from current page
            page_assets = self.extract_assets_from_page()

            # Add only new assets (avoid duplicates)
            new_assets = [a for a in page_assets if a not in all_assets]
            all_assets.extend(new_assets)

            print(f"  Total unique assets so far: {len(all_assets)}")

            # Try to go to next page
            if not self.click_next_page():
                print(f"\n✓ No more pages. Captured {len(all_assets)} total assets.\n")
                break

            page_num += 1

        print(f"\n{'='*70}")
        print(f"✓ CAPTURED {len(all_assets)} TOTAL ASSETS")
        print(f"{'='*70}\n")

        # Show first 20
        if all_assets:
            print("First 20 assets:")
            for i, name in enumerate(all_assets[:20], 1):
                print(f"  {i}. {name}")
            if len(all_assets) > 20:
                print(f"  ... and {len(all_assets) - 20} more")

        return all_assets

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
        print("Usage: python3 final_complete_asset_capture.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    rnd_url = "https://acme.egalvanic-rnd.com"
    ai_url = "https://acme.egalvanic.ai"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Capture RND
    print("\n" + "="*70)
    print("STEP 1: CAPTURING FROM RND")
    print("="*70)

    capturer_rnd = CompleteAssetCapture()
    try:
        rnd_assets = capturer_rnd.capture_all_assets(rnd_url, email, password)
        rnd_file = f"FINAL_RND_ASSETS_{timestamp}.json"
        with open(rnd_file, 'w') as f:
            json.dump(rnd_assets, f, indent=2)
        print(f"\n✓ Saved: {rnd_file}")
    finally:
        capturer_rnd.close()

    # Capture AI
    print("\n" + "="*70)
    print("STEP 2: CAPTURING FROM AI")
    print("="*70)

    capturer_ai = CompleteAssetCapture()
    try:
        ai_assets = capturer_ai.capture_all_assets(ai_url, email, password)
        ai_file = f"FINAL_AI_ASSETS_{timestamp}.json"
        with open(ai_file, 'w') as f:
            json.dump(ai_assets, f, indent=2)
        print(f"\n✓ Saved: {ai_file}")
    finally:
        capturer_ai.close()

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
            'missing_from_ai_count': len(missing_from_ai),
            'new_in_ai_count': len(new_in_ai)
        },
        'missing_from_ai': missing_from_ai,
        'new_in_ai': new_in_ai,
        'common_assets': common[:50],  # First 50 common assets
        'timestamp': datetime.now().isoformat()
    }

    comparison_file = f"FINAL_ASSET_COMPARISON_{timestamp}.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison, f, indent=2)

    # Print summary
    print(f"{'='*70}")
    print(f"FINAL COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"RND Total:               {len(rnd_assets)}")
    print(f"AI Total:                {len(ai_assets)}")
    print(f"Difference:              {len(ai_assets) - len(rnd_assets):+d}")
    print(f"Common Assets:           {len(common)}")
    print(f"Missing from AI:         {len(missing_from_ai)}")
    print(f"New in AI:               {len(new_in_ai)}")
    print(f"{'='*70}")

    if missing_from_ai:
        print(f"\n🚨 ASSETS MISSING FROM AI ({len(missing_from_ai)} total):")
        for i, asset in enumerate(missing_from_ai, 1):
            print(f"  {i}. ❌ {asset}")
        print()

    if new_in_ai:
        print(f"➕ NEW ASSETS IN AI ({len(new_in_ai)} total):")
        for i, asset in enumerate(new_in_ai, 1):
            print(f"  {i}. ✓ {asset}")
        print()

    print(f"✓ Comparison saved: {comparison_file}\n")

    # Generate simple HTML report with asset names
    html_file = f"FINAL_MISSING_ASSETS_REPORT_{timestamp}.html"
    with open(html_file, 'w') as f:
        f.write(generate_html_report(comparison))
    print(f"✓ HTML report: {html_file}\n")

def generate_html_report(comp):
    """Generate HTML report"""
    s = comp['summary']
    missing = comp['missing_from_ai']
    new = comp['new_in_ai']

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Final Asset Comparison - Missing Assets Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid; }}
        .stat-number {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .critical {{ border-color: #dc3545; }} .critical .stat-number {{ color: #dc3545; }}
        .warning {{ border-color: #fd7e14; }} .warning .stat-number {{ color: #fd7e14; }}
        .success {{ border-color: #28a745; }} .success .stat-number {{ color: #28a745; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .asset-list {{ columns: 3; column-gap: 20px; }}
        .asset-item {{ break-inside: avoid; padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; border-left: 3px solid #dc3545; }}
        .asset-item-new {{ border-left-color: #28a745; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Final Asset Comparison Report</h1>
        <p>Complete asset-by-asset comparison between RND and AI environments</p>
        <p style="font-size: 14px; opacity: 0.9;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{s['rnd_total']}</div>
                <div>RND Assets</div>
            </div>
            <div class="stat">
                <div class="stat-number">{s['ai_total']}</div>
                <div>AI Assets</div>
            </div>
            <div class="stat {'warning' if s['difference'] != 0 else 'success'}">
                <div class="stat-number">{s['difference']:+d}</div>
                <div>Difference</div>
            </div>
            <div class="stat success">
                <div class="stat-number">{s['common']}</div>
                <div>Common</div>
            </div>
            <div class="stat {'critical' if s['missing_from_ai_count'] > 0 else 'success'}">
                <div class="stat-number">{s['missing_from_ai_count']}</div>
                <div>Missing from AI</div>
            </div>
            <div class="stat {'warning' if s['new_in_ai_count'] > 0 else 'success'}">
                <div class="stat-number">{s['new_in_ai_count']}</div>
                <div>New in AI</div>
            </div>
        </div>
    </div>
"""

    if missing:
        html += f"""
    <div class="section">
        <h2>🚨 Assets Missing from AI ({len(missing)} assets)</h2>
        <p style="color: #721c24; background: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545;">
            <strong>CRITICAL:</strong> These assets exist in RND but are MISSING from AI.
        </p>
        <div class="asset-list">
"""
        for i, asset in enumerate(missing, 1):
            html += f'            <div class="asset-item"><strong>{i}.</strong> {asset}</div>\n'
        html += """        </div>
    </div>
"""

    if new:
        html += f"""
    <div class="section">
        <h2>➕ New Assets in AI ({len(new)} assets)</h2>
        <p style="color: #856404; background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107;">
            <strong>INFO:</strong> These assets exist in AI but NOT in RND.
        </p>
        <div class="asset-list">
"""
        for i, asset in enumerate(new, 1):
            html += f'            <div class="asset-item asset-item-new"><strong>{i}.</strong> {asset}</div>\n'
        html += """        </div>
    </div>
"""

    if not missing and not new:
        html += """
    <div class="section">
        <h2>✅ Perfect Match!</h2>
        <p style="color: #155724; background: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745;">
            All assets match perfectly between RND and AI environments.
        </p>
    </div>
"""

    html += """
    <div style="text-align: center; padding: 20px; color: #6c757d; font-size: 12px;">
        <p>Final Asset Comparison Report</p>
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    main()
