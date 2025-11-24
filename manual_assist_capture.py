#!/usr/bin/env python3
"""
MANUAL ASSIST CAPTURE
This script opens the browser but lets YOU do the login and navigation.
Then it captures the data.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import os
from datetime import datetime

def manual_assist_capture(url, output_name):
    print(f"\n{'='*80}")
    print(f"CAPTURING: {url}")
    print('='*80)
    
    # Setup Chrome - VISIBLE
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    # Enable performance logging
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🌐 Navigating to: {url}")
        driver.get(url)
        
        print("\n" + "!"*80)
        print("PLEASE LOG IN MANUALLY IN THE BROWSER WINDOW")
        print("Navigate to the Dashboard where the sites are listed.")
        print("Make sure 'Super Caremark' or other sites are visible.")
        print("!"*80)
        
        input("\nPress Enter here AFTER you have logged in and the dashboard is loaded...")
        
        print("\n🔄 Capturing data...")
        
        # Capture network logs
        logs = driver.get_log('performance')
        api_responses = []
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if log['method'] == 'Network.responseReceived':
                    response = log['params']['response']
                    if '/api/' in response['url']:
                        try:
                            request_id = log['params']['requestId']
                            body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            data = json.loads(body['body'])
                            api_responses.append({'url': response['url'], 'response': data})
                        except:
                            pass
            except:
                continue
                
        print(f"✅ Captured {len(api_responses)} API responses")
        
        # Save
        os.makedirs(output_name, exist_ok=True)
        with open(f"{output_name}/complete_capture.json", 'w') as f:
            json.dump({'api_responses': api_responses}, f, indent=2)
            
        return output_name
        
    finally:
        driver.quit()

def main():
    print("MANUAL ASSIST CAPTURE TOOL")
    
    # RND
    rnd_out = manual_assist_capture("https://acme.egalvanic-rnd.com", "rnd_manual_capture")
    
    # AI
    ai_out = manual_assist_capture("https://acme.egalvanic.ai", "ai_manual_capture")
    
    # Compare
    os.system(f"python3 site_data_comparator.py {rnd_out} {ai_out}")
    os.system("open site_comparison_report.html")

if __name__ == "__main__":
    main()
