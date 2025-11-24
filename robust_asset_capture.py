#!/usr/bin/env python3
"""
ROBUST ASSET CAPTURE
Uses auto-login and page scraping to ensure we get the asset list.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import json
import time
import os
import sys

def login(driver, url, username, password):
    print(f"🔐 Logging in to {url}...")
    driver.get(url)
    time.sleep(3)
    
    try:
        # Check if already logged in
        if "dashboard" in driver.current_url:
            print("✅ Already logged in")
            return True
            
        # Email
        email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email.clear()
        email.send_keys(username)
        
        # Password
        try:
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
        except:
            # Maybe 2-step login?
            email.send_keys(Keys.RETURN)
            time.sleep(2)
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
        print("⏳ Waiting for dashboard...")
        time.sleep(10)
        return True
        
    except Exception as e:
        print(f"⚠️  Login issue: {e}")
        print("Please finish logging in manually...")
        time.sleep(15)
        return True

def capture_assets_from_page(driver, site_name):
    print(f"\n🔍 Capturing assets for {site_name}...")
    
    # Wait for user to navigate if needed
    print(f"👉 Please navigate to {site_name} -> ASSETS page")
    print("   (I'll wait 30 seconds for you to do this)")
    
    # Wait loop with countdown
    for i in range(30, 0, -5):
        print(f"   {i} seconds remaining...")
        time.sleep(5)
        
    print("📸 Scraping page content...")
    
    assets = []
    
    # Strategy 1: Look for table rows
    try:
        rows = driver.find_elements(By.TAG_NAME, "tr")
        if len(rows) > 1:
            print(f"   Found {len(rows)} table rows")
            headers = [th.text.lower() for th in rows[0].find_elements(By.TAG_NAME, "th")]
            
            for row in rows[1:]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    asset = {}
                    # Try to map columns to headers
                    for i, col in enumerate(cols):
                        text = col.text.strip()
                        if i < len(headers):
                            asset[headers[i]] = text
                        else:
                            asset[f"col_{i}"] = text
                    
                    # If we found a name, keep it
                    if asset:
                        assets.append(asset)
    except:
        pass
        
    # Strategy 2: Look for cards/list items
    if not assets:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, ".asset-item, .list-item, .card")
            for item in items:
                text = item.text
                if text:
                    assets.append({'raw_text': text})
        except:
            pass
            
    print(f"✅ Scraped {len(assets)} assets from page")
    return assets

def compare(old_assets, new_assets):
    print("\n" + "="*80)
    print("COMPARISON RESULT")
    print("="*80)
    print(f"Old Count: {len(old_assets)}")
    print(f"New Count: {len(new_assets)}")
    
    # Simple count comparison
    diff = len(new_assets) - len(old_assets)
    if diff > 0:
        print(f"🟢 +{diff} assets in New environment")
    elif diff < 0:
        print(f"🔴 {diff} assets in New environment")
    else:
        print("✅ Counts match")

def main():
    username = "rahul+acme@egalvanic.com"
    password = "RP@egalvanic123"
    
    chrome_options = Options()
    # chrome_options.add_argument('--headless') # Visible mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. RND
        print("\nSTEP 1: RND Website")
        login(driver, "https://acme.egalvanic-rnd.com", username, password)
        old_assets = capture_assets_from_page(driver, "Super Caremark")
        
        # 2. AI
        print("\nSTEP 2: AI Website")
        login(driver, "https://acme.egalvanic.ai", username, password)
        new_assets = capture_assets_from_page(driver, "Super Caremark")
        
        # 3. Compare
        compare(old_assets, new_assets)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
