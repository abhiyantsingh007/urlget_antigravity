#!/usr/bin/env python3
"""
Direct API Capture - Gets data directly from API endpoints
Much more reliable than UI automation
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
import os
from datetime import datetime

def capture_via_api(base_url, username, password, output_dir="api_direct_capture"):
    """Capture data by monitoring API calls after login"""
    
    print("\n" + "="*80)
    print("DIRECT API CAPTURE")
    print("="*80)
    
    # Setup Chrome with network logging
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = None
    api_data = {}
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print(f"\n🌐 Navigating to: {base_url}")
        driver.get(base_url)
        time.sleep(3)
        
        # Login
        print(f"🔐 Logging in as: {username}")
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
            
            print("⏳ Waiting for dashboard to load...")
            time.sleep(8)  # Give time for API calls to complete
            
        except Exception as e:
            print(f"Login step error: {e}")
        
        # Capture all network traffic
        print("\n📡 Capturing API responses...")
        logs = driver.get_log('performance')
        
        api_responses = []
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                
                # Look for API responses
                if log['method'] == 'Network.responseReceived':
                    response_data = log['params']['response']
                    url = response_data['url']
                    
                    # Only capture our API endpoints
                    if '/api/' in url and response_data.get('mimeType') == 'application/json':
                        request_id = log['params']['requestId']
                        
                        try:
                            # Get the response body
                            response_body = driver.execute_cdp_cmd('Network.getResponseBody', {
                                'requestId': request_id
                            })
                            
                            body = json.loads(response_body['body'])
                            
                            api_responses.append({
                                'url': url,
                                'timestamp': log['params']['timestamp'],
                                'response': body
                            })
                            
                            # Extract endpoint name for display
                            import re
                            endpoint = re.sub(r'https?://[^/]+', '', url)
                            endpoint = re.sub(r'\?.*', '', endpoint)
                            print(f"  ✓ {endpoint}")
                            
                        except Exception as e:
                            # Some responses might not be available
                            pass
                            
            except Exception as e:
                continue
        
        print(f"\n✅ Captured {len(api_responses)} API responses")
        
        # Extract site data from the responses
        sites_data = {}
        user_id = None
        
        # Find user ID from /api/auth/me
        for resp in api_responses:
            if '/api/auth/me' in resp['url']:
                user_id = resp['response'].get('id')
                print(f"📋 User ID: {user_id}")
                break
        
        # Get list of sites from /api/users/{user_id}/slds
        sites_list = []
        for resp in api_responses:
            if '/api/users/' in resp['url'] and '/slds' in resp['url']:
                sites_list = resp['response']
                print(f"📋 Found {len(sites_list)} sites in account")
                break
        
        # For each site, try to find its overview data
        for resp in api_responses:
            if '/api/lookup/site-overview/' in resp['url']:
                site_data = resp['response']
                site_name = site_data.get('name', 'Unknown')
                
                # Extract metrics
                sites_data[site_name] = {
                    'name': site_name,
                    'total_assets': site_data.get('total_assets', 0),
                    'open_issues': site_data.get('open_issues_count', 0),
                    'active_sessions': site_data.get('active_sessions_count', 0),
                }
                
                print(f"  • {site_name}: {sites_data[site_name]['total_assets']} assets")
        
        # If no overview data, use the sites list
        if not sites_data and sites_list:
            print("\n💡 Using sites list (no detailed metrics available)")
            for site in sites_list:
                site_name = site.get('name', 'Unknown')
                sites_data[site_name] = {
                    'name': site_name,
                    'total_assets': 0,  # Will need manual entry
                }
        
        # Save data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"{output_dir}_{timestamp}"
        os.makedirs(output_path, exist_ok=True)
        
        output_file = os.path.join(output_path, "complete_capture.json")
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'capture_time': datetime.now().isoformat(),
                    'base_url': base_url,
                    'total_sites': len(sites_data),
                    'total_api_responses': len(api_responses)
                },
                'api_responses': [{
                    'url': base_url,
                    'response': {
                        'sites': sites_data
                    }
                }],
                'raw_api_responses': api_responses
            }, f, indent=2)
        
        print(f"\n✅ Saved to: {output_file}")
        print(f"📁 Output directory: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if driver:
            driver.quit()

def main():
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python3 api_direct_capture.py <url> <username> <password>")
        sys.exit(1)
    
    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    
    print("="*80)
    print("COMPREHENSIVE SITE CAPTURE VIA API")
    print("="*80)
    
    # Capture RND
    print("\n🔵 CAPTURING RND WEBSITE...")
    rnd_output = capture_via_api(url, username, password, "rnd_api_capture")
    
    if not rnd_output:
        print("\n❌ Failed to capture RND site")
        sys.exit(1)
    
    # Ask about AI site
    response = input("\n\nCapture AI website? (y/n): ").strip().lower()
    if response == 'y':
        ai_url = input("AI website URL (or Enter for egalvanic.ai): ").strip()
        if not ai_url:
            ai_url = url.replace('egalvanic-rnd.com', 'egalvanic.ai')
        
        print(f"\n🔴 CAPTURING AI WEBSITE...")
        ai_output = capture_via_api(ai_url, username, password, "ai_api_capture")
        
        if ai_output:
            print("\n" + "="*80)
            print("COMPARING SITES")
            print("="*80)
            os.system(f"python3 site_data_comparator.py {rnd_output} {ai_output}")
            print("\n✅ Comparison complete!")
            print("📄 Open site_comparison_report.html")
    
    print(f"\n✅ Capture complete!")

if __name__ == "__main__":
    main()
