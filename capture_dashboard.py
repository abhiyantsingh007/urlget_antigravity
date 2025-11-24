#!/usr/bin/env python3
"""
DASHBOARD DATA CAPTURE
Captures the main dashboard showing all sites and their metrics (assets, issues, etc.)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import json
import time
import os
from datetime import datetime

def capture_dashboard_data(base_url, username, password, output_dir="dashboard_capture"):
    """Capture dashboard data showing all sites"""
    
    print("\n" + "="*80)
    print("DASHBOARD DATA CAPTURE")
    print("="*80)
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}_{timestamp}"
    os.makedirs(output_path, exist_ok=True)
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Enable performance logging to capture network requests
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = None
    api_responses = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print(f"\n📱 Navigating to: {base_url}")
        driver.get(base_url)
        time.sleep(3)
        
        # Login
        print(f"🔐 Logging in as: {username}")
        try:
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            password_field = driver.find_element(By.NAME, "password")
            
            email_field.send_keys(username)
            password_field.send_keys(password)
            
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            print("⏳ Waiting for dashboard to load...")
            time.sleep(5)
            
        except TimeoutException:
            print("⚠️  No login form found - might already be logged in or different flow")
        
        # Wait for dashboard elements
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("✅ Dashboard loaded")
        except:
            print("⚠️  Dashboard might not have loaded properly")
        
        # Capture network logs
        print("\n📡 Capturing API responses...")
        logs = driver.get_log('performance')
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # Look for network responses
                if log['method'] == 'Network.responseReceived':
                    response_url = log['params']['response']['url']
                    
                    # Filter for API responses
                    if '/api/' in response_url and log['params']['response']['mimeType'] == 'application/json':
                        request_id = log['params']['requestId']
                        
                        # Try to get response body
                        try:
                            response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            body = json.loads(response_body['body'])
                            
                            api_responses.append({
                                'url': response_url,
                                'timestamp': log['params']['timestamp'],
                                'response': body
                            })
                            
                            print(f"  ✓ Captured: {response_url}")
                            
                        except Exception as e:
                            # Response body might not be available for all requests
                            pass
                            
            except Exception as e:
                continue
        
        # Save API responses
        output_file = os.path.join(output_path, "dashboard_data.json")
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'capture_time': datetime.now().isoformat(),
                    'base_url': base_url,
                    'total_responses': len(api_responses)
                },
                'api_responses': api_responses
            }, f, indent=2)
        
        print(f"\n✅ Captured {len(api_responses)} API responses")
        print(f"📁 Saved to: {output_file}")
        
        # Save screenshot
        screenshot_path = os.path.join(output_path, "dashboard_screenshot.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        return output_path
        
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
    
    if len(sys.argv) < 3:
        print("Usage: python3 capture_dashboard.py <base_url> <username> [password]")
        print("\nExample:")
        print("  python3 capture_dashboard.py https://acme.egalvanic-rnd.com user@example.com mypassword")
        sys.exit(1)
    
    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3] if len(sys.argv) > 3 else input("Password: ")
    
    # Capture old site
    print("\n🔵 Capturing OLD site dashboard...")
    old_output = capture_dashboard_data(base_url, username, password, "old_dashboard_capture")
    
    # Ask if they want to capture new site
    response = input("\n\nCapture NEW site dashboard? (y/n): ").strip().lower()
    if response == 'y':
        new_url = input("New site URL (or press Enter to use same): ").strip()
        if not new_url:
            new_url = base_url
        
        print("\n🔴 Capturing NEW site dashboard...")
        new_output = capture_dashboard_data(new_url, username, password, "new_dashboard_capture")
        
        # Run comparison
        if old_output and new_output:
            print("\n\n" + "="*80)
            print("Running site comparison...")
            print("="*80)
            os.system(f"python3 site_data_comparator.py {old_output} {new_output}")
    
    print("\n✅ Capture complete!")

if __name__ == "__main__":
    main()
