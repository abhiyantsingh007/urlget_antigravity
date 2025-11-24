#!/usr/bin/env python3
"""
Automated Migration Data Capture
Captures all API responses from a website for migration verification
"""
import json
import os
import time
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def capture_website_data(base_url, email, password, output_name):
    """Capture all data from a website"""
    print(f"\n{'='*60}")
    print(f"Capturing data from: {base_url}")
    print(f"{'='*60}\n")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless=new")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Install ChromeDriver automatically
    chromedriver_autoinstaller.install()
    driver = webdriver.Chrome(options=chrome_options)
    
    all_api_responses = []
    
    try:
        # Login
        print(f"1. Logging in to {base_url}...")
        driver.get(f"{base_url}/login")
        time.sleep(2)
        
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        print("   ✓ Login successful\n")
        time.sleep(3)
        
        # Pages to visit
        pages = [
            "/dashboard",
            "/sites",
            "/assets",
            "/issues",
            "/reports"
        ]
        
        print("2. Visiting pages and capturing API responses...")
        for page in pages:
            try:
                print(f"   Visiting {page}...")
                driver.get(f"{base_url}{page}")
                time.sleep(6)  # Wait longer for APIs to load
                
                # If on dashboard, try to interact with site dropdown to load site data
                if page == "/dashboard":
                    try:
                        # Look for site dropdown and click it to load site list
                        site_dropdown = driver.find_element(By.CSS_SELECTOR, "select, .dropdown-toggle, [class*='site'], [class*='dropdown']")
                        site_dropdown.click()
                        time.sleep(3)
                        
                        # Try to select first few sites to trigger their API calls
                        options = driver.find_elements(By.CSS_SELECTOR, "option, .dropdown-item, li")
                        for opt in options[:5]:  # Try first 5 sites
                            try:
                                opt.click()
                                time.sleep(2)
                            except:
                                pass
                    except:
                        print("      Could not interact with site dropdown")
                
                # Capture network logs
                logs = driver.get_log('performance')
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        if (message['message']['method'] == 'Network.responseReceived' and 
                            'response' in message['message']['params']):
                            
                            response = message['message']['params']['response']
                            url = response['url']
                            
                            # Only capture API calls that succeeded
                            if ('/api/' in url and response['status'] == 200):
                                try:
                                    driver.execute_cdp_cmd('Network.enable', {})
                                    request_id = message['message']['params']['requestId']
                                    result = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                    body = result.get('body', '')
                                    
                                    if result.get('base64Encoded', False):
                                        import base64
                                        body = base64.b64decode(body).decode('utf-8')
                                    
                                    try:
                                        body = json.loads(body)
                                    except:
                                        pass
                                    
                                    # Check if this API response already captured (avoid duplicates)
                                    url_clean = url.split('?')[0]  # Remove query params for comparison
                                    if not any(r['url'].split('?')[0] == url_clean and r['response'] == body for r in all_api_responses):
                                        api_entry = {
                                            'url': url,
                                            'timestamp': datetime.now().isoformat(),
                                            'response': body
                                        }
                                        all_api_responses.append(api_entry)
                                        print(f"      ✓ Captured: {url.split('/api/')[-1][:50]}...")
                                except:
                                    pass
                    except:
                        continue
                        
            except Exception as e:
                print(f"   ⚠ Error visiting {page}: {e}")
        
        # Save all responses
        output_file = f"{output_name}_capture.json"
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'base_url': base_url,
                    'capture_time': datetime.now().isoformat(),
                    'total_api_responses': len(all_api_responses)
                },
                'api_responses': all_api_responses
            }, f, indent=2)
        
        print(f"\n3. Capture complete!")
        print(f"   Total API responses captured: {len(all_api_responses)}")
        print(f"   Data saved to: {output_file}\n")
        
        return output_file
        
    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture website data for migration verification')
    parser.add_argument('--url', required=True, help='Website URL')
    parser.add_argument('--email', default="rahul+acme@egalvanic.com", help='Login email')
    parser.add_argument('--password', default="RP@egalvanic123", help='Login password')
    parser.add_argument('--output', required=True, help='Output file prefix (old or new)')
    
    args = parser.parse_args()
    capture_website_data(args.url, args.email, args.password, args.output)
