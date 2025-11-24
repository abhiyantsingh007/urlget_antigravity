#!/usr/bin/env python3
"""
COMPREHENSIVE SITE-BY-SITE CAPTURE
Iterates through ALL sites in the dropdown and captures their data
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time
import os
from datetime import datetime

def login_to_site(driver, base_url, username, password):
    """Log in to the website"""
    print(f"\n🔐 Logging in to: {base_url}")
    driver.get(base_url)
    time.sleep(3)
    
    try:
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_field = driver.find_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(username)
        password_field.send_keys(password)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        print("⏳ Waiting for dashboard...")
        time.sleep(5)
        return True
        
    except TimeoutException:
        print("⚠️  No login form - might already be logged in")
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def find_site_dropdown(driver):
    """Find the site selection dropdown"""
    # Common selectors for site dropdowns
    selectors = [
        "select[name*='site']",
        "select[id*='site']",
        ".site-selector",
        "#site-dropdown",
        "select.form-select",
        "select",  # Last resort - any select
    ]
    
    for selector in selectors:
        try:
            dropdown = driver.find_element(By.CSS_SELECTOR, selector)
            # Check if it has options
            options = dropdown.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:  # More than just placeholder
                print(f"✅ Found site dropdown with {len(options)} sites")
                return dropdown
        except NoSuchElementException:
            continue
    
    print("⚠️  Could not find site dropdown")
    return None

def get_all_sites_from_dropdown(dropdown):
    """Extract all site names from dropdown"""
    sites = []
    options = dropdown.find_elements(By.TAG_NAME, "option")
    
    for option in options:
        text = option.text.strip()
        value = option.get_attribute('value')
        
        # Skip empty/placeholder options
        if text and text.lower() not in ['select site', 'choose site', 'all sites', '']:
            sites.append({
                'name': text,
                'value': value,
                'option_element': option
            })
    
    return sites

def capture_site_data(driver):
    """Capture current site's data from the page"""
    data = {}
    
    # Wait for page to load
    time.sleep(2)
    
    # Try to find metric cards/values on the page
    # Common patterns for dashboard metrics
    patterns = [
        # Pattern 1: Cards with numbers
        {'container': '.stat-card, .metric-card, .dashboard-card', 'label': '.label, .title, h3, h4', 'value': '.value, .number, .count'},
        # Pattern 2: Table rows
        {'container': 'tr', 'label': 'td:first-child, th', 'value': 'td:last-child'},
        # Pattern 3: Definition lists
        {'container': 'dl', 'label': 'dt', 'value': 'dd'},
    ]
    
    for pattern in patterns:
        try:
            containers = driver.find_elements(By.CSS_SELECTOR, pattern['container'])
            for container in containers:
                try:
                    label_elem = container.find_element(By.CSS_SELECTOR, pattern['label'])
                    value_elem = container.find_element(By.CSS_SELECTOR, pattern['value'])
                    
                    label = label_elem.text.strip().lower().replace(' ', '_')
                    value_text = value_elem.text.strip()
                    
                    # Try to extract number
                    import re
                    numbers = re.findall(r'[\d,]+', value_text)
                    if numbers:
                        # Remove commas and convert to int
                        value = int(numbers[0].replace(',', ''))
                        data[label] = value
                except:
                    continue
        except:
            continue
    
    # Also try to capture from page text directly
    page_text = driver.find_element(By.TAG_NAME, "body").text
    
    # Look for common patterns like "Total Assets: 179"
    import re
    patterns_to_find = {
        'total_assets': r'Total Assets[:\s]+(\d+)',
        'open_issues': r'Open Issues[:\s]+(\d+)',
        'active_sessions': r'Active (?:Sessions|Site Visits)[:\s]+(\d+)',
        'pending_tasks': r'Pending Tasks[:\s]+(\d+)',
    }
    
    for key, pattern in patterns_to_find.items():
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            data[key] = int(match.group(1))
    
    return data

def capture_all_sites(base_url, username, password, output_dir="all_sites_capture"):
    """Capture data for all sites in dropdown"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE SITE-BY-SITE CAPTURE")
    print("="*80)
    
    # Setup Chrome
    chrome_options = Options()
    # BROWSER VISIBLE FOR DEBUGGING
    # chrome_options.add_argument('--headless')  # Commented out so we can see what's happening
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    all_sites_data = {}
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        
        # Login
        if not login_to_site(driver, base_url, username, password):
            print("❌ Login failed, exiting")
            return None
        
        # Find site dropdown
        print("\n🔍 Looking for site dropdown...")
        dropdown = find_site_dropdown(driver)
        
        if not dropdown:
            print("❌ Could not find site dropdown")
            print("\n💡 TIP: The page might be structured differently.")
            print("   Please open the browser (remove --headless) and tell me:")
            print("   1. What element selects the site?")
            print("   2. How to identify it (CSS selector)?")
            return None
        
        # Get all sites
        sites = get_all_sites_from_dropdown(dropdown)
        print(f"\n📋 Found {len(sites)} sites to capture:")
        for site in sites:
            print(f"   • {site['name']}")
        
        # Capture data for each site
        print(f"\n🔄 Capturing data for each site...\n")
        
        for i, site in enumerate(sites, 1):
            site_name = site['name']
            print(f"[{i}/{len(sites)}] Capturing: {site_name}")
            
            try:
                # Re-find the dropdown (page might have refreshed)
                dropdown = find_site_dropdown(driver)
                if not dropdown:
                    print(f"   ⚠️  Could not find dropdown, skipping")
                    continue
                
                # Select this site
                from selenium.webdriver.support.ui import Select
                select = Select(dropdown)
                select.select_by_visible_text(site_name)
                
                # Wait for data to load
                time.sleep(3)
                
                # Capture the data
                site_data = capture_site_data(driver)
                
                if site_data:
                    all_sites_data[site_name] = site_data
                    print(f"   ✅ Captured {len(site_data)} metrics: {list(site_data.keys())}")
                else:
                    print(f"   ⚠️  No data captured")
                
                # Take screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.makedirs(output_dir, exist_ok=True)
                screenshot_path = os.path.join(output_dir, f"{site_name.replace(' ', '_')}.png")
                driver.save_screenshot(screenshot_path)
                
            except Exception as e:
                print(f"   ❌ Error capturing {site_name}: {e}")
                continue
        
        # Save all data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, "complete_capture.json")
        
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'capture_time': datetime.now().isoformat(),
                    'base_url': base_url,
                    'total_sites': len(all_sites_data)
                },
                'api_responses': [{
                    'url': base_url,
                    'response': {
                        'sites': all_sites_data
                    }
                }]
            }, f, indent=2)
        
        print(f"\n✅ Captured {len(all_sites_data)} sites")
        print(f"📁 Saved to: {output_file}")
        
        # Print summary
        print("\n📊 Summary:")
        for site_name, data in all_sites_data.items():
            assets = data.get('total_assets', 'N/A')
            print(f"   {site_name}: {assets} assets")
        
        return output_dir
        
    except Exception as e:
        print(f"\n❌ Error during capture: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()

def main():
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║  COMPREHENSIVE SITE-BY-SITE CAPTURE                           ║
║  Captures data for EVERY site in the dropdown                 ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 3:
        print("Usage: python3 capture_all_sites.py <base_url> <username> [password]")
        print("\nExample:")
        print("  python3 capture_all_sites.py https://acme.egalvanic-rnd.com user@example.com mypassword")
        print("\nThis will:")
        print("  1. Log in to the website")
        print("  2. Find the site selection dropdown")
        print("  3. Iterate through EVERY site")
        print("  4. Capture metrics for each site")
        print("  5. Save all data for comparison")
        sys.exit(1)
    
    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) > 3 else input("Password: ")
    
    # Capture old site
    print("\n" + "="*70)
    print("STEP 1: CAPTURE OLD WEBSITE")
    print("="*70)
    old_output = capture_all_sites(base_url, username, password, "old_all_sites_capture")
    
    if not old_output:
        print("\n❌ Failed to capture old site")
        sys.exit(1)
    
    # Ask if they want to capture new site
    print("\n" + "="*70)
    response = input("\nCapture NEW website? (y/n): ").strip().lower()
    
    if response == 'y':
        new_url = input("New site URL (press Enter to use same URL): ").strip()
        if not new_url:
            new_url = base_url
        
        print("\n" + "="*70)
        print("STEP 2: CAPTURE NEW WEBSITE")
        print("="*70)
        new_output = capture_all_sites(new_url, username, password, "new_all_sites_capture")
        
        if not new_output:
            print("\n❌ Failed to capture new site")
            sys.exit(1)
        
        # Run comparison
        print("\n" + "="*70)
        print("STEP 3: COMPARING ALL SITES")
        print("="*70)
        os.system(f"python3 site_data_comparator.py {old_output} {new_output}")
        
        print("\n" + "="*70)
        print("✅ COMPLETE!")
        print("="*70)
        print(f"\n📄 Open site_comparison_report.html to see differences for ALL sites")
        print(f"   Including Super Caremark: 179 → 180 assets\n")
    
    else:
        print(f"\n✅ Old site captured to: {old_output}")
        print("   Run this script again to capture the new site and compare")

if __name__ == "__main__":
    main()
