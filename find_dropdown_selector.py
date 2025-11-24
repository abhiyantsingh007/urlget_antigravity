#!/usr/bin/env python3
"""
FIND DROPDOWN SELECTOR
Dumps HTML around the site name to find the dropdown trigger.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def main():
    username = "rahul+acme@egalvanic.com"
    password = "RP@egalvanic123"
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://acme.egalvanic-rnd.com")
        
        # Login
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        print("🔐 Logging in...")
        email = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email.clear()
        email.send_keys(username)
        email.send_keys(Keys.RETURN)
        time.sleep(2)
        pwd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        pwd.send_keys(password)
        pwd.send_keys(Keys.RETURN)
        
        print("⏳ Waiting for dashboard...")
        time.sleep(10)
        
        print("🔍 Dumping HTML around 'Super Caremark'...")
        # Find element containing the text
        try:
            el = driver.find_element(By.XPATH, "//*[contains(text(), 'Super Caremark')]")
            # Get parent HTML
            parent = el.find_element(By.XPATH, "./..")
            grandparent = parent.find_element(By.XPATH, "./..")
            
            print("\nHTML Snippet:")
            print(grandparent.get_attribute('outerHTML'))
            
            # Also look for anything that looks like a dropdown arrow
            arrows = driver.find_elements(By.CSS_SELECTOR, "svg, i, .icon")
            print(f"\nFound {len(arrows)} icons that might be dropdown arrows")
            
        except Exception as e:
            print(f"Error finding element: {e}")
            print("Dumping body start...")
            print(driver.find_element(By.TAG_NAME, "body").get_attribute('innerHTML')[:2000])
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
