#!/usr/bin/env python3
"""
CAPTURE ALL SITES ASSETS
Iterates through ALL sites in the dropdown and compares their assets.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re
import json
import os

def login(driver, username, password):
    print("🔐 Auto-logging in...")
    try:
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
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
        except:
            email.send_keys(Keys.RETURN)
            time.sleep(2)
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
        print("⏳ Waiting for dashboard...")
        WebDriverWait(driver, 20).until(EC.url_contains("dashboard"))
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Login flow note: {e}")

def get_all_sites(driver):
    print("🔍 Finding all sites...")
    sites = []
    
    # Try to find the site selector dropdown
    # Usually it displays the current site name
    try:
        # Look for elements that might be the dropdown trigger
        # Common patterns: arrow icons, current site name
        triggers = driver.find_elements(By.CSS_SELECTOR, "[role='button'], .dropdown-trigger, .select-trigger")
        
        # Filter for ones near the top/header
        header_triggers = [t for t in triggers if t.location['y'] < 150 and t.is_displayed()]
        
        dropdown_opened = False
        for trigger in header_triggers:
            try:
                trigger.click()
                time.sleep(1)
                # Check if a list appeared
                options = driver.find_elements(By.CSS_SELECTOR, "[role='option'], .dropdown-item, .select-option")
                if len(options) > 1:
                    print(f"   Found dropdown with {len(options)} options")
                    for opt in options:
                        text = opt.text.strip()
                        if text and text not in ["Logout", "Settings", "Profile"]:
                            sites.append(text)
                    dropdown_opened = True
                    # Close it
                    trigger.click()
                    break
            except:
                continue
                
        if not dropdown_opened:
            # Fallback: Just return the ones we know for sure + generic ones found in text
            print("⚠️ Could not auto-detect dropdown. Using known sites list.")
            return ["Super Caremark", "Site657", "All Facilities", "London, UK", "Toronto, Canada", "Melbourne, AU"]
            
    except Exception as e:
        print(f"⚠️ Error finding sites: {e}")
        return ["Super Caremark", "Site657", "All Facilities"]
        
    return list(set(sites))

def select_site_via_dropdown(driver, site_name):
    """Select a site from the autocomplete dropdown.
    Uses explicit waits for the dropdown button and the list option.
    """
    try:
        # Wait for the dropdown button (aria-label='Open') to be clickable
        open_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Open']"))
        )
        open_btn.click()
        # Wait for the list item matching the site name
        option = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space(.)='{site_name}']"))
        )
        option.click()
        # Give the page a moment to load the new site data
        time.sleep(4)
        print(f"✅ Site '{site_name}' selected via dropdown")
        return True
    except Exception as e:
        print(f"⚠️ Could not select site '{site_name}' via dropdown: {e}")
        return False

# Replace calls to select_site with select_site_via_dropdown throughout the script


def navigate_to_assets(driver):
    # Same as before
    xpath_options = ["//span[contains(text(), 'Assets')]", "//div[contains(text(), 'Assets')]"]
    for xpath in xpath_options:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    el.click()
                    time.sleep(5)
                    return True
        except:
            continue
    return False

def capture_site_data(driver, site_name):
    print(f"📸 Capturing data for {site_name}...")
    
    # 1. Select Site
    # Since selecting is hard, we'll try to verify if we are on the right site
    if site_name not in driver.page_source:
        print(f"⚠️ Warning: '{site_name}' text not found on page. Might be on wrong site.")
        
    # 2. Go to Assets
    navigate_to_assets(driver)
    
    # 3. Capture
    text = driver.find_element(By.TAG_NAME, "body").text
    match = re.search(r'(\d+)\s+assets', text)
    count = int(match.group(1)) if match else 0
    
    return count, text

def extract_names(text):
    # Same heuristic as before
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    names = []
    try:
        start_idx = -1
        for i, line in enumerate(lines):
            if "Asset Name" in line:
                start_idx = i + 1
                break
        if start_idx != -1:
            i = start_idx
            while i < len(lines):
                line = lines[i]
                if line not in ["—", "1", "2", "3", "Complete", "Active", "Circuit Breaker"]:
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
    
    results = {}
    
    try:
        # 1. RND
        print("\n" + "="*60)
        print("PHASE 1: RND Website")
        print("="*60)
        driver.get("https://acme.egalvanic-rnd.com")
        login(driver, username, password)
        
        # Get list of sites (hardcoded for reliability if auto-detect fails)
        sites = ["Super Caremark", "Site657", "All Facilities"] 
        # You can add more here if you know them
        
        rnd_data = {}
        for site in sites:
            # Use automated dropdown selection
            if not select_site_via_dropdown(driver, site):
                print(f"⚠️ Falling back to manual selection for {site}")
                input("   Press Enter after you manually select the site...")
            
            count, text = capture_site_data(driver, site)
            names = extract_names(text)
            rnd_data[site] = {'count': count, 'names': names}
            print(f"✅ {site}: {count} assets")

        # 2. AI
        print("\n" + "="*60)
        print("PHASE 2: AI Website")
        print("="*60)
        driver.get("https://acme.egalvanic.ai")
        login(driver, username, password)
        
        ai_data = {}
        for site in sites:
            # Use automated dropdown selection
            if not select_site_via_dropdown(driver, site):
                print(f"⚠️ Falling back to manual selection for {site}")
                input("   Press Enter after you manually select the site...")
            
            count, text = capture_site_data(driver, site)
            names = extract_names(text)
            ai_data[site] = {'count': count, 'names': names}
            print(f"✅ {site}: {count} assets")
            
        # 3. Compare
        print("\n" + "="*60)
        print("FULL COMPARISON REPORT")
        print("="*60)
        
        for site in sites:
            r = rnd_data.get(site, {'count': 0, 'names': set()})
            a = ai_data.get(site, {'count': 0, 'names': set()})
            
            diff = a['count'] - r['count']
            icon = "✅" if diff == 0 else "🔴" if diff < 0 else "🟢"
            
            print(f"\n{icon} {site}")
            print(f"   RND: {r['count']} -> AI: {a['count']} (Diff: {diff})")
            
            added = a['names'] - r['names']
            missing = r['names'] - a['names']
            
            if added:
                print(f"   ➕ Added: {', '.join(list(added)[:5])}" + ("..." if len(added)>5 else ""))
            if missing:
                print(f"   ➖ Missing: {', '.join(list(missing)[:5])}" + ("..." if len(missing)>5 else ""))

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
