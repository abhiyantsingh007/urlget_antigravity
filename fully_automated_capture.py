#!/usr/bin/env python3
"""
FULLY AUTOMATED ASSET CAPTURE
1. Auto-login
2. Auto-navigate to 'Assets'
3. Capture asset count and list
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re

def login(driver, username, password):
    print("🔐 Auto-logging in...")
    try:
        # Check if already logged in
        try:
            WebDriverWait(driver, 3).until(EC.url_contains("dashboard"))
            print("✅ Already logged in")
            return
        except:
            pass

        email = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email.clear()
        email.send_keys(username)
        
        try:
            # Try single page login
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
        except:
            # Try two-step login
            email.send_keys(Keys.RETURN)
            time.sleep(2)
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
        print("⏳ Waiting for dashboard...")
        WebDriverWait(driver, 20).until(EC.url_contains("dashboard"))
        time.sleep(5) # Extra wait for full load
    except Exception as e:
        print(f"⚠️ Login flow note: {e}")

def navigate_to_assets(driver):
    print("🧭 Navigating to Assets page...")
    
    # Try to find "Assets" link in sidebar
    xpath_options = [
        "//div[contains(text(), 'Assets')]",
        "//span[contains(text(), 'Assets')]",
        "//a[contains(text(), 'Assets')]",
        "//p[contains(text(), 'Assets')]"
    ]
    
    found = False
    for xpath in xpath_options:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    print(f"   Clicking 'Assets' (found via {xpath})")
                    el.click()
                    found = True
                    break
            if found: break
        except:
            continue
            
    if not found:
        print("⚠️ Could not auto-click 'Assets'. Please click it manually.")
        return False
        
    # Wait for asset list header or count
    print("⏳ Waiting for asset list to load...")
    time.sleep(5)
    return True

def select_site(driver, site_name):
    print(f"🏭 Attempting to select site: {site_name}")
    # This is hard to automate without DOM, but we'll try to find the site name if it's already selected
    # or find a dropdown.
    
    # Check if site is already visible
    if site_name in driver.page_source:
        print(f"   '{site_name}' text found on page. Assuming correct site or accessible.")
    else:
        print(f"⚠️ '{site_name}' not found on page. You might need to select it manually if not already selected.")

def capture_asset_data(driver):
    print("📸 Capturing asset data...")
    
    # Get full text
    text = driver.find_element(By.TAG_NAME, "body").text
    
    # Look for "X assets" pattern
    match = re.search(r'(\d+)\s+assets', text)
    count = 0
    if match:
        count = int(match.group(1))
        print(f"✅ Found asset count: {count}")
    else:
        print("⚠️ Could not find 'X assets' text pattern.")
        
    return count, text

def extract_asset_names(text):
    """
    Heuristic to extract asset names from the text dump.
    Based on the pattern: Name -> QR -> Condition -> Class -> Building
    """
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    names = []
    
    # Find start of data
    try:
        start_idx = -1
        for i, line in enumerate(lines):
            if "Asset Name" in line and "QR Code" in lines[i+1]:
                start_idx = i + 1 # Skip header line
                # Skip other headers if they appear sequentially
                while start_idx < len(lines) and lines[start_idx] in ["QR Code", "Condition", "Asset Class", "Building"]:
                    start_idx += 1
                break
        
        if start_idx != -1:
            # Simple heuristic: The first line of every block of 5-6 lines is likely the name
            # This depends on the exact layout, but let's try to capture lines that look like names
            # "CB 175", "—", "1", "Circuit Breaker", "—"
            
            i = start_idx
            while i < len(lines):
                line = lines[i]
                # Filter out obvious non-names
                if line not in ["—", "1", "2", "3", "4", "5", "Complete", "Active", "Circuit Breaker", "Panelboard", "Disconnect Switch"]:
                    # Also check length
                    if len(line) > 2 and len(line) < 50:
                        names.append(line)
                i += 1
    except:
        pass
        
    return set(names)

def main():
    username = "rahul+acme@egalvanic.com"
    password = "RP@egalvanic123"
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # RND
        print("\n" + "="*60)
        print("STEP 1: RND Website")
        print("="*60)
        driver.get("https://acme.egalvanic-rnd.com")
        login(driver, username, password)
        select_site(driver, "Super Caremark")
        navigate_to_assets(driver)
        rnd_count, rnd_text = capture_asset_data(driver)
        rnd_names = extract_asset_names(rnd_text)
        print(f"📋 Extracted {len(rnd_names)} potential asset names")
        
        # AI
        print("\n" + "="*60)
        print("STEP 2: AI Website")
        print("="*60)
        driver.get("https://acme.egalvanic.ai")
        login(driver, username, password)
        select_site(driver, "Super Caremark")
        navigate_to_assets(driver)
        ai_count, ai_text = capture_asset_data(driver)
        ai_names = extract_asset_names(ai_text)
        print(f"📋 Extracted {len(ai_names)} potential asset names")
        
        # Compare
        print("\n" + "="*60)
        print("FINAL COMPARISON")
        print("="*60)
        print(f"RND Assets: {rnd_count}")
        print(f"AI Assets:  {ai_count}")
        
        diff = ai_count - rnd_count
        if diff > 0:
            print(f"🔴 RESULT: +{diff} assets in AI website")
        elif diff < 0:
            print(f"🔴 RESULT: {diff} assets in AI website")
        else:
            print("✅ RESULT: Asset counts match")
            
        # Name Comparison
        print("\n🔍 ASSET NAME ANALYSIS:")
        added = ai_names - rnd_names
        missing = rnd_names - ai_names
        
        if added:
            print("\n🟢 POTENTIAL ADDED ASSETS (In AI, not in RND):")
            for name in added:
                print(f"  + {name}")
                
        if missing:
            print("\n🔴 POTENTIAL MISSING ASSETS (In RND, not in AI):")
            for name in missing:
                print(f"  - {name}")
                
        if not added and not missing:
            print("  (No name differences detected in visible text)")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
