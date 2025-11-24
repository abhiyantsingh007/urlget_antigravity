#!/usr/bin/env python3
"""
WORKING Site Switcher - Actually switches between all sites!
Uses the Material-UI Autocomplete that was discovered
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

def login(driver, base_url, email, password):
    """Login to the website"""
    print(f"🔐 Logging in to {base_url}...")
    driver.get(f"{base_url}/login")
    time.sleep(2)

    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
    print("✅ Logged in successfully")
    time.sleep(3)

def get_all_sites(driver):
    """Get list of all available sites from the autocomplete dropdown"""
    print("\n🔍 Getting list of all sites...")

    try:
        # Find the MUI Autocomplete input (placeholder="Select facility")
        autocomplete_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Select facility']"))
        )

        # Click to open dropdown
        autocomplete_input.click()
        time.sleep(1)

        # Get all options
        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[role='option']"))
        )

        sites = []
        for opt in options:
            site_name = opt.text.strip()
            if site_name:
                sites.append(site_name)

        # Close dropdown by pressing Escape
        autocomplete_input.send_keys(Keys.ESCAPE)
        time.sleep(1)

        print(f"✅ Found {len(sites)} sites:")
        for site in sites:
            print(f"   • {site}")

        return sites

    except Exception as e:
        print(f"❌ Error getting sites: {e}")
        return []

def select_site(driver, site_name):
    """Select a specific site from the autocomplete dropdown"""
    try:
        # Find the autocomplete input
        autocomplete_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Select facility']"))
        )

        # Clear and type the site name
        autocomplete_input.click()
        time.sleep(0.5)
        autocomplete_input.clear()
        autocomplete_input.send_keys(site_name)
        time.sleep(1)

        # Wait for the option to appear and click it
        option_xpath = f"//li[@role='option' and contains(text(), '{site_name}')]"
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        option.click()

        # Wait for page to load new data
        time.sleep(3)

        return True

    except Exception as e:
        print(f"   ❌ Error selecting site '{site_name}': {e}")
        return False

def capture_site_data(driver, site_name):
    """Capture data for the currently selected site"""
    data = {
        "site_name": site_name,
        "timestamp": datetime.now().isoformat(),
        "metrics": {}
    }

    try:
        # Get the page text
        body_text = driver.find_element(By.TAG_NAME, "body").text

        # Look for common metrics
        import re
        patterns = {
            'total_assets': r'Total Assets[:\s]+(\d+)',
            'active_assets': r'Active Assets[:\s]+(\d+)',
            'total_sites': r'Total (?:Sites|Facilities)[:\s]+(\d+)',
            'open_issues': r'Open Issues[:\s]+(\d+)',
            'completion': r'(\d+)%\s*completion',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, body_text, re.IGNORECASE)
            if match:
                data['metrics'][key] = int(match.group(1))

        # Also capture visible numbers in cards
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, ".MuiCard-root, [class*='Card']")
            for i, card in enumerate(cards[:10]):
                card_text = card.text
                numbers = re.findall(r'\d+', card_text)
                if numbers and len(card_text) < 200:
                    data['metrics'][f'card_{i}'] = card_text[:100]
        except:
            pass

    except Exception as e:
        print(f"   ⚠️  Error capturing data: {e}")

    return data

def capture_all_sites(base_url, email, password, output_file="site_capture.json"):
    """Main function to capture data from all sites"""

    print("\n" + "="*80)
    print("AUTOMATED SITE SWITCHING & DATA CAPTURE")
    print(f"Website: {base_url}")
    print("="*80 + "\n")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Visible browser so you can see it working
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Login
        login(driver, base_url, email, password)

        # Get all available sites
        sites = get_all_sites(driver)

        if not sites:
            print("❌ Could not find any sites!")
            return None

        # Capture data for each site
        all_data = []

        print(f"\n🔄 Switching through {len(sites)} sites and capturing data...\n")

        for i, site_name in enumerate(sites, 1):
            print(f"[{i}/{len(sites)}] Switching to: {site_name}")

            # Select the site
            if select_site(driver, site_name):
                print(f"   ✅ Site selected successfully")

                # Capture data
                site_data = capture_site_data(driver, site_name)
                all_data.append(site_data)

                # Take screenshot
                screenshot_name = f"site_{site_name.replace(' ', '_').replace('/', '_')}.png"
                driver.save_screenshot(screenshot_name)
                print(f"   📸 Screenshot: {screenshot_name}")

                if site_data['metrics']:
                    print(f"   📊 Captured metrics: {list(site_data['metrics'].keys())}")

            else:
                print(f"   ⚠️  Skipped")

            print()

        # Save all data
        output_data = {
            "metadata": {
                "base_url": base_url,
                "capture_time": datetime.now().isoformat(),
                "total_sites": len(all_data)
            },
            "sites": all_data
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print("="*80)
        print(f"✅ SUCCESS! Captured data from {len(all_data)} sites")
        print(f"📁 Data saved to: {output_file}")
        print("="*80)

        # Print summary
        print("\n📊 SUMMARY:")
        for site_data in all_data:
            assets = site_data['metrics'].get('total_assets', 'N/A')
            print(f"   {site_data['site_name']}: {assets} assets")

        return output_file

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        driver.quit()

if __name__ == "__main__":
    import sys

    print("""
╔════════════════════════════════════════════════════════════════╗
║  WORKING SITE SWITCHER                                         ║
║  Actually switches between ALL sites automatically!            ║
╚════════════════════════════════════════════════════════════════╝
    """)

    # Configuration
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"

    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    if len(sys.argv) > 2:
        EMAIL = sys.argv[2]
    if len(sys.argv) > 3:
        PASSWORD = sys.argv[3]

    output_file = "rnd_site_capture.json" if "rnd" in BASE_URL else "ai_site_capture.json"

    result = capture_all_sites(BASE_URL, EMAIL, PASSWORD, output_file)

    if result:
        print("\n✅ Done! You can now run this script again with the new website URL")
        print("   to capture the AI website and compare them.")
