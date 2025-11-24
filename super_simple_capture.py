#!/usr/bin/env python3
"""
SUPER SIMPLE CAPTURE
Just dumps the text content of the page.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def login(driver, username, password):
    print("🔐 Auto-logging in...")
    try:
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
            
        print("⏳ Waiting for login...")
        time.sleep(5)
    except Exception as e:
        print(f"⚠️ Login skipped/failed: {e}")

def capture_text(driver, url, label):
    print(f"\n{'='*80}")
    print(f"CAPTURING: {label}")
    print(f"URL: {url}")
    print('='*80)
    
    driver.get(url)
    login(driver, "rahul+acme@egalvanic.com", "RP@egalvanic123")
    
    print("\n👉 Please NAVIGATE to the ASSETS LIST")
    input("Press Enter when the list is visible...")
    
    print("\n📸 Capturing page text...")
    
    # Get full page text
    text = driver.find_element(By.TAG_NAME, "body").text
    
    # Save it
    filename = f"{label.lower().replace(' ', '_')}_text.txt"
    with open(filename, "w") as f:
        f.write(text)
        
    print(f"✅ Saved page text to {filename} ({len(text)} chars)")
    
    # Try to find asset-like lines
    lines = text.split('\n')
    asset_lines = [l for l in lines if len(l) > 10 and len(l) < 100] # Heuristic
    
    print(f"   Found {len(asset_lines)} lines of text")
    return asset_lines

def main():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # RND
        rnd_lines = capture_text(driver, "https://acme.egalvanic-rnd.com", "RND Assets")
        
        # AI
        ai_lines = capture_text(driver, "https://acme.egalvanic.ai", "AI Assets")
        
        # Compare
        print("\n" + "="*80)
        print("TEXT COMPARISON")
        print("="*80)
        
        rnd_set = set(rnd_lines)
        ai_set = set(ai_lines)
        
        diff = ai_set - rnd_set
        if diff:
            print(f"Found {len(diff)} lines in AI that are not in RND:")
            for line in list(diff)[:20]:
                print(f"  + {line}")
        else:
            print("No unique text found in AI page.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
