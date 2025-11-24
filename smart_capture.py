#!/usr/bin/env python3
"""
Smart Migration Capture - Navigates through all sites and captures their dashboard data
"""
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller

def smart_capture(base_url, email, password, output_file):
    """Capture data by actually clicking through sites"""
    print(f"\n{'='*60}")
    print(f"Smart capture from: {base_url}")
    print(f"{'='*60}\n")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Remove headless to see what's happening
    # chrome_options.add_argument("--headless=new")
    
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=chrome_options)
    
    captured_sites = {}
    
    try:
        # Login
        print("1. Logging in...")
        driver.get(f"{base_url}/login")
        time.sleep(2)
        
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        print("   ✓ Logged in\n")
        time.sleep(3)
        
        # Go to dashboard
        driver.get(f"{base_url}/dashboard")
        time.sleep(5)
        
        print("2. Looking for site dropdown...")
        
        # Try to find and click site dropdown
        try:
            # Look for dropdown button/select
            dropdown = driver.find_element(By.CSS_SELECTOR, "select, button[aria-label*='site' i], button[aria-haspopup='listbox'], [role='button']")
            dropdown.click()
            time.sleep(2)
            
            # Get all site options
            options = driver.find_elements(By.CSS_SELECTOR, "option, li[role='option'], .MuiMenuItem-root, [role='menuitem']")
            
            print(f"   Found {len(options)} options\n")
            
            # Capture each site
            for i, option in enumerate(options):
                try:
                    site_text = option.text.strip()
                    if not site_text or len(site_text) > 50:
                        continue
                        
                    print(f"3. Selecting site: {site_text}")
                    
                    # Click the option
                    option.click()
                    time.sleep(4)  # Wait for dashboard to update
                    
                    # Extract dashboard metrics from page text
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    
                    # Look for total assets in the page
                    import re
                    
                    site_info = {
                        "name": site_text,
                        "total_assets": None,
                        "page_text_sample": body_text[:500]
                    }
                    
                    # Try to find "Total Assets" or similar metrics
                    patterns = [
                        r'Total Assets?\s*[:\-]?\s*(\d+)',
                        r'Assets?\s*[:\-]?\s*(\d+)',
                        r'(\d+)\s*Total Assets?',
                        r'(\d+)\s*Assets?'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, body_text, re.IGNORECASE)
                        if match:
                            site_info['total_assets'] = int(match.group(1))
                            break
                    
                    captured_sites[site_text] = site_info
                    print(f"   ✓ Captured (Total Assets: {site_info['total_assets']})")
                    
                    # Re-open dropdown for next iteration
                    if i < len(options) - 1:
                        dropdown = driver.find_element(By.CSS_SELECTOR, "select, button[aria-label*='site' i], button[aria-haspopup='listbox'], [role='button']")
                        dropdown.click()
                        time.sleep(2)
                    
                except Exception as e:
                    print(f"   ✗ Error with option {i}: {e}")
                    continue
            
        except Exception as e:
            print(f"   Could not find dropdown: {e}")
            print("   Trying to extract from current page...")
            
            # Fallback: just extract from current page
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"   Page text sample: {body_text[:500]}")
        
        # Save results
        output = {
            "metadata": {
                "base_url": base_url,
                "capture_time": datetime.now().isoformat(),
                "total_sites": len(captured_sites)
            },
            "sites": captured_sites
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Captured {len(captured_sites)} sites to {output_file}")
        return output_file
        
    finally:
        time.sleep(2)
        driver.quit()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python smart_capture.py <url> <output_file>")
        print("Example: python smart_capture.py https://acme.egalvanic-rnd.com smart_old.json")
        sys.exit(1)
    
    url = sys.argv[1]
    output = sys.argv[2]
    
    smart_capture(url, "rahul+acme@egalvanic.com", "RP@egalvanic123", output)
