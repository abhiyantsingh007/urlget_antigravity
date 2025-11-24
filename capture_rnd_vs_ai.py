#!/usr/bin/env python3
"""
Simple Two-Website Capture
Captures from RND and AI websites properly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import json
import time
import os
from datetime import datetime

def simple_capture(url, username, password, output_name):
    """Simple capture with better error handling"""
    
    print(f"\n{'='*80}")
    print(f"CAPTURING: {url}")
    print('='*80)
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        print(f"✅ Loaded: {url}")
        time.sleep(3)
        
        # Try to log in
        try:
            # Wait for email field
            email = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            # Clear and type slowly
            email.clear()
            time.sleep(0.5)
            email.send_keys(username)
            time.sleep(0.5)
            
            # Password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(password)
            time.sleep(0.5)
            
            # Click submit
            password_field.send_keys(Keys.RETURN)
            
            print("🔐 Login submitted, waiting for dashboard...")
            time.sleep(15)  # Generous wait for login redirect
            
            # FORCE RELOAD to ensure we capture the initial dashboard load API calls
            print("🔄 Refreshing page to capture dashboard load...")
            driver.refresh()
            time.sleep(10)
            
        except Exception as e:
            print(f"⚠️  Login flow: {e}")
            print("Continuing anyway...")
        
        # Capture network logs
        print("📡 Capturing API responses...")
        logs = driver.get_log('performance')
        
        api_responses = []
        sites_data = {}
        
        # We need to filter logs carefully
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                if log['method'] == 'Network.responseReceived':
                    response = log['params']['response']
                    response_url = response['url']
                    
                    # Capture ALL API calls that might contain data
                    if '/api/' in response_url:
                        request_id = log['params']['requestId']
                        
                        try:
                            # Only try to get body for JSON responses
                            if 'json' in response.get('mimeType', '') or 'text/plain' in response.get('mimeType', ''):
                                body = driver.execute_cdp_cmd('Network.getResponseBody', {
                                    'requestId': request_id
                                })
                                
                                data = json.loads(body['body'])
                                api_responses.append({
                                    'url': response_url,
                                    'response': data
                                })
                                
                                # Extract endpoint name
                                import re
                                endpoint = re.sub(r'https?://[^/]+', '', response_url)
                                endpoint = re.sub(r'\?.*', '', endpoint)
                                print(f"  ✓ {endpoint}")
                        except:
                            pass
            except:
                continue
        
        # Try to extract sites data
        for resp in api_responses:
            if '/slds' in resp['url']:
                sites_list = resp['response']
                print(f"\n📋 Found {len(sites_list)} sites:")
                for site in sites_list[:10]:
                    if isinstance(site, dict):
                        name = site.get('name', 'Unknown')
                        print(f"   • {name}")
                        sites_data[name] = {
                            'name': name,
                            'total_assets': 0  # Will need to be filled
                        }
        
        # Save
        os.makedirs(output_name, exist_ok=True)
        output_file = os.path.join(output_name, 'complete_capture.json')
        
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'url': url,
                    'capture_time': datetime.now().isoformat(),
                    'total_responses': len(api_responses)
                },
                'api_responses': [{
                    'url': url,
                    'response': {'sites': sites_data}
                }] if sites_data else api_responses
            }, f, indent=2)
        
        print(f"\n✅ Saved to: {output_file}")
        print(f"📊 Captured {len(api_responses)} API responses")
        
        return output_name
        
    finally:
        driver.quit()

def main():
    username = "rahul+acme@egalvanic.com"
    password = "RP@egalvanic123"
    
    print("\n" + "="*80)
    print("TWO-WEBSITE COMPARISON CAPTURE")
    print("="*80)
    print("\nRND: https://acme.egalvanic-rnd.com")
    print("AI:  https://acme.egalvanic.ai")
    print("="*80)
    
    # Capture RND
    rnd_output = simple_capture(
        "https://acme.egalvanic-rnd.com",
        username,
        password,
        "rnd_website_capture"
    )
    
    if not rnd_output:
        print("\n❌ RND capture failed")
        return
    
    input("\n\nPress Enter to capture AI website...")
    
    # Capture AI
    ai_output = simple_capture(
        "https://acme.egalvanic.ai",
        username,
        password,
        "ai_website_capture"
    )
    
    if not ai_output:
        print("\n❌ AI capture failed")
        return
    
    # Compare
    print("\n" + "="*80)
    print("COMPARING WEBSITES")
    print("="*80)
    
    os.system(f"python3 site_data_comparator.py {rnd_output} {ai_output}")
    
    print("\n✅ COMPLETE!")
    print("📄 Open: site_comparison_report.html")
    os.system("open site_comparison_report.html")

if __name__ == "__main__":
    main()
