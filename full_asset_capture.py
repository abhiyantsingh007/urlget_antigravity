"""
Complete Asset Capture Script with API-based approach
Captures all assets by intercepting network requests or using proper selectors
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

class FullAssetCapture:
    def __init__(self):
        self.rnd_url = "https://acme.egalvanic-rnd.com"
        self.ai_url = "https://acme.egalvanic.ai"
        self.driver = None

    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        # Run in visible mode to see what's happening
        # options.add_argument('--headless')

        # Enable logging to see network requests
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

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
            email_field = WebDriverWait(self.driver, 10).until(
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
        """Navigate to Assets page"""
        print(f"\n🔍 Navigating to Assets page...")

        try:
            # Try multiple selectors for Assets link
            selectors = [
                "//a[contains(text(), 'Assets')]",
                "//span[contains(text(), 'Assets')]/..",
                "//div[contains(text(), 'Assets')]",
                "//nav//a[@href*='asset']"
            ]

            for selector in selectors:
                try:
                    assets_link = self.driver.find_element(By.XPATH, selector)
                    assets_link.click()
                    time.sleep(3)
                    print(f"✓ Navigated to Assets page")
                    return True
                except:
                    continue

            # If all fail, try direct URL
            current_url = self.driver.current_url
            base_url = current_url.split('/dashboard')[0] if '/dashboard' in current_url else current_url.split('/site')[0]

            # Try common asset URL patterns
            asset_urls = [
                f"{base_url}/assets",
                f"{base_url}/site/assets",
                f"{base_url}/data/assets"
            ]

            for asset_url in asset_urls:
                self.driver.get(asset_url)
                time.sleep(3)

                # Check if we got to assets page
                if "asset" in self.driver.current_url.lower() or "Assets" in self.driver.page_source:
                    print(f"✓ Navigated to Assets page via URL: {asset_url}")
                    return True

            print(f"✗ Could not navigate to Assets")
            return False

        except Exception as e:
            print(f"✗ Navigation error: {str(e)}")
            return False

    def get_page_source_assets(self):
        """Extract assets from page source"""
        print(f"\n📄 Extracting assets from page source...")

        # Save page source for inspection
        page_source = self.driver.page_source

        # Try to find table data using multiple approaches
        assets = []

        try:
            # Method 1: Try to find table rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            print(f"Found {len(rows)} table rows")

            for idx, row in enumerate(rows):
                try:
                    cells = row.find_elements(By.CSS_SELECTOR, "td")

                    if len(cells) >= 4:
                        # Extract text from cells
                        asset_data = {
                            "index": idx + 1,
                            "asset_name": cells[0].text.strip(),
                            "qr_code": cells[1].text.strip() if len(cells) > 1 else "",
                            "condition": cells[2].text.strip() if len(cells) > 2 else "",
                            "asset_class": cells[3].text.strip() if len(cells) > 3 else "",
                            "building": cells[4].text.strip() if len(cells) > 4 else ""
                        }

                        # Only add if asset name exists
                        if asset_data["asset_name"] and asset_data["asset_name"] != "—":
                            assets.append(asset_data)
                            print(f"  {idx+1}. {asset_data['asset_name']}")

                except Exception as e:
                    continue

            # Method 2: If no rows found, try different selectors
            if len(assets) == 0:
                print("Trying alternative selectors...")

                # Try MUI table
                rows = self.driver.find_elements(By.CSS_SELECTOR, ".MuiTableBody-root tr")
                print(f"Found {len(rows)} MUI table rows")

                for idx, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "td, .MuiTableCell-root")

                        if len(cells) >= 4:
                            asset_data = {
                                "index": idx + 1,
                                "asset_name": cells[0].text.strip(),
                                "qr_code": cells[1].text.strip() if len(cells) > 1 else "",
                                "condition": cells[2].text.strip() if len(cells) > 2 else "",
                                "asset_class": cells[3].text.strip() if len(cells) > 3 else "",
                                "building": cells[4].text.strip() if len(cells) > 4 else ""
                            }

                            if asset_data["asset_name"] and asset_data["asset_name"] != "—":
                                assets.append(asset_data)
                                print(f"  {idx+1}. {asset_data['asset_name']}")

                    except Exception as e:
                        continue

            # Method 3: Try div-based tables
            if len(assets) == 0:
                print("Trying div-based table...")
                rows = self.driver.find_elements(By.CSS_SELECTOR, "[role='row']")
                print(f"Found {len(rows)} role=row elements")

                for idx, row in enumerate(rows):
                    try:
                        cells = row.find_elements(By.CSS_SELECTOR, "[role='cell']")

                        if len(cells) >= 4:
                            asset_data = {
                                "index": idx + 1,
                                "asset_name": cells[0].text.strip(),
                                "qr_code": cells[1].text.strip() if len(cells) > 1 else "",
                                "condition": cells[2].text.strip() if len(cells) > 2 else "",
                                "asset_class": cells[3].text.strip() if len(cells) > 3 else "",
                                "building": cells[4].text.strip() if len(cells) > 4 else ""
                            }

                            if asset_data["asset_name"] and asset_data["asset_name"] != "—" and asset_data["asset_name"] != "Asset Name":
                                assets.append(asset_data)
                                print(f"  {idx+1}. {asset_data['asset_name']}")

                    except Exception as e:
                        continue

        except Exception as e:
            print(f"Error extracting assets: {str(e)}")

        print(f"\n✓ Extracted {len(assets)} assets from current page")
        return assets

    def scroll_and_load_all(self):
        """Scroll down to load all assets if using infinite scroll"""
        print(f"\n📜 Scrolling to load all assets...")

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

        print(f"✓ Finished scrolling")

    def change_rows_per_page(self, rows=100):
        """Try to change rows per page to maximum"""
        print(f"\n⚙ Attempting to set rows per page to {rows}...")

        try:
            # Try to find and click the rows per page dropdown
            selectors = [
                "//select[contains(@aria-label, 'Rows per page')]",
                "//div[contains(text(), 'Rows per page')]/following-sibling::*//select",
                "//*[contains(text(), '25')]/ancestor::div[contains(@role, 'button')]"
            ]

            for selector in selectors:
                try:
                    dropdown = self.driver.find_element(By.XPATH, selector)
                    dropdown.click()
                    time.sleep(1)

                    # Try to select 100
                    option = self.driver.find_element(By.XPATH, f"//option[@value='{rows}'] | //li[contains(text(), '{rows}')]")
                    option.click()
                    time.sleep(3)

                    print(f"✓ Set to {rows} rows per page")
                    return True
                except:
                    continue

        except Exception as e:
            print(f"⚠ Could not change rows per page: {str(e)}")

        return False

    def click_next_page(self):
        """Click next page button"""
        try:
            next_buttons = [
                "//button[@aria-label='Next page']",
                "//button[contains(@aria-label, 'next')]",
                "//button[contains(text(), 'Next')]",
                "//*[@aria-label='Go to next page']"
            ]

            for selector in next_buttons:
                try:
                    button = self.driver.find_element(By.XPATH, selector)

                    # Check if button is enabled
                    if button.is_enabled() and not button.get_attribute("disabled"):
                        button.click()
                        time.sleep(3)
                        return True
                except:
                    continue

            return False

        except:
            return False

    def capture_all_assets(self, site_name):
        """Main capture function with pagination"""
        print(f"\n{'='*60}")
        print(f"📦 CAPTURING ALL ASSETS")
        print(f"{'='*60}")

        all_assets = []

        # Try to maximize rows per page first
        self.change_rows_per_page(100)

        # Also try scrolling
        self.scroll_and_load_all()

        page = 1
        while True:
            print(f"\n📄 Processing Page {page}...")

            # Extract assets from current page
            assets = self.get_page_source_assets()

            if len(assets) == 0:
                print(f"⚠ No assets found on page {page}")

                if page == 1:
                    # Save screenshot for debugging
                    screenshot_file = f"assets_page_debug_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_file)
                    print(f"📸 Saved screenshot: {screenshot_file}")

                    # Save page source
                    with open(f"assets_page_source_{int(time.time())}.html", 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print(f"💾 Saved page source for debugging")

                break

            # Add to collection (avoid duplicates)
            new_assets = 0
            for asset in assets:
                # Check if asset already exists
                exists = False
                for existing in all_assets:
                    if existing['asset_name'] == asset['asset_name']:
                        exists = True
                        break

                if not exists:
                    all_assets.append(asset)
                    new_assets += 1

            print(f"✓ Added {new_assets} new assets (Total: {len(all_assets)})")

            # Try to go to next page
            if not self.click_next_page():
                print(f"\n✓ No more pages. Finished!")
                break

            page += 1

            # Safety limit
            if page > 20:
                print(f"\n⚠ Reached page limit")
                break

        print(f"\n{'='*60}")
        print(f"✓ CAPTURE COMPLETE: {len(all_assets)} assets")
        print(f"{'='*60}")

        return all_assets

    def run(self, email, password, site_name):
        """Main execution"""
        try:
            print(f"\n{'#'*70}")
            print(f"# FULL ASSET CAPTURE TOOL")
            print(f"{'#'*70}")
            print(f"Site: {site_name}")
            print(f"Email: {email}")
            print(f"{'#'*70}\n")

            self.setup_driver()

            # Capture RND
            print(f"\n{'='*70}")
            print(f"🔵 RND WEBSITE")
            print(f"{'='*70}")

            if not self.login(self.rnd_url, email, password):
                print("Failed to login to RND")
                return

            if not self.navigate_to_assets():
                print("Failed to navigate to assets")
                return

            rnd_assets = self.capture_all_assets(site_name)

            # Save RND assets
            rnd_file = f"rnd_complete_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(rnd_file, 'w', encoding='utf-8') as f:
                json.dump(rnd_assets, f, indent=2)
            print(f"\n💾 Saved: {rnd_file}")

            # Capture AI
            print(f"\n{'='*70}")
            print(f"🟣 AI WEBSITE")
            print(f"{'='*70}")

            if not self.login(self.ai_url, email, password):
                print("Failed to login to AI")
                return

            if not self.navigate_to_assets():
                print("Failed to navigate to assets")
                return

            ai_assets = self.capture_all_assets(site_name)

            # Save AI assets
            ai_file = f"ai_complete_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(ai_file, 'w', encoding='utf-8') as f:
                json.dump(ai_assets, f, indent=2)
            print(f"\n💾 Saved: {ai_file}")

            # Generate comparison
            print(f"\n{'='*70}")
            print(f"📊 GENERATING COMPARISON")
            print(f"{'='*70}")

            self.generate_detailed_comparison(rnd_assets, ai_assets)

        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                print(f"\n🚪 Closing browser...")
                input("Press Enter to close browser...")
                self.driver.quit()

    def generate_detailed_comparison(self, rnd_assets, ai_assets):
        """Generate detailed comparison report"""

        # Create asset name sets
        rnd_names = {asset['asset_name'] for asset in rnd_assets}
        ai_names = {asset['asset_name'] for asset in ai_assets}

        only_in_rnd = rnd_names - ai_names
        only_in_ai = ai_names - rnd_names
        common = rnd_names & ai_names

        # Create dictionaries for easy lookup
        rnd_dict = {asset['asset_name']: asset for asset in rnd_assets}
        ai_dict = {asset['asset_name']: asset for asset in ai_assets}

        # Find field differences
        field_differences = []
        for name in common:
            rnd_asset = rnd_dict[name]
            ai_asset = ai_dict[name]

            diffs = {}
            for field in ['qr_code', 'condition', 'asset_class', 'building']:
                if rnd_asset.get(field, '') != ai_asset.get(field, ''):
                    diffs[field] = {
                        'rnd': rnd_asset.get(field, ''),
                        'ai': ai_asset.get(field, '')
                    }

            if diffs:
                field_differences.append({
                    'asset_name': name,
                    'differences': diffs
                })

        print(f"\nRND Assets: {len(rnd_assets)}")
        print(f"AI Assets: {len(ai_assets)}")
        print(f"Common: {len(common)}")
        print(f"Only in RND: {len(only_in_rnd)}")
        print(f"Only in AI: {len(only_in_ai)}")
        print(f"Field Differences: {len(field_differences)}")

        # Save comparison
        comparison = {
            'summary': {
                'rnd_total': len(rnd_assets),
                'ai_total': len(ai_assets),
                'common': len(common),
                'only_in_rnd': len(only_in_rnd),
                'only_in_ai': len(only_in_ai),
                'field_differences': len(field_differences)
            },
            'only_in_rnd': sorted(list(only_in_rnd)),
            'only_in_ai': sorted(list(only_in_ai)),
            'field_differences': field_differences
        }

        comp_file = f"detailed_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(comp_file, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)

        print(f"\n💾 Saved comparison: {comp_file}")
        print(f"\n✓ Done! Check the JSON files for complete data.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python full_asset_capture.py <email> <password> <site_name>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    site_name = sys.argv[3]

    capturer = FullAssetCapture()
    capturer.run(email, password, site_name)
