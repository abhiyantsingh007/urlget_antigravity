#!/usr/bin/env python3
"""
ASSET DETAIL CAPTURE & COMPARATOR
Captures full list of assets (names, IDs, details) for deep comparison.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import os
import sys

def capture_assets(url, site_name, output_dir):
    print(f"\n{'='*80}")
    print(f"CAPTURING ASSETS FOR: {site_name}")
    print(f"URL: {url}")
    print('='*80)
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        
        print("\n" + "!"*80)
        print(f"PLEASE NAVIGATE TO THE ASSETS LIST FOR '{site_name}'")
        print("1. Log in")
        print(f"2. Select site: {site_name}")
        print("3. Click on 'Assets' tab/page")
        print("4. Scroll down to ensure all assets are loaded (if lazy loaded)")
        print("!"*80)
        
        input("\nPress Enter here AFTER the asset list is fully visible...")
        
        print("\n🔄 Capturing asset data...")
        
        # Capture network logs to find asset API calls
        logs = driver.get_log('performance')
        assets = []
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])['message']
                if log['method'] == 'Network.responseReceived':
                    response = log['params']['response']
                    # Look for asset-related endpoints
                    if '/api/' in response['url'] and ('asset' in response['url'] or 'equipment' in response['url']):
                        try:
                            request_id = log['params']['requestId']
                            body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            data = json.loads(body['body'])
                            
                            # Try to find list of assets in response
                            items = []
                            if isinstance(data, list):
                                items = data
                            elif isinstance(data, dict):
                                items = data.get('assets', []) or data.get('items', []) or data.get('data', [])
                            
                            if items and isinstance(items, list):
                                print(f"  ✓ Found {len(items)} items in {response['url']}")
                                assets.extend(items)
                        except:
                            pass
            except:
                continue
        
        # Remove duplicates based on ID or Name
        unique_assets = {}
        for asset in assets:
            if not isinstance(asset, dict): continue
            
            # Try to find a unique ID
            asset_id = asset.get('id') or asset.get('_id') or asset.get('asset_id') or asset.get('name')
            if asset_id:
                unique_assets[asset_id] = asset
        
        print(f"\n✅ Captured {len(unique_assets)} unique assets")
        
        # Save
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "assets.json")
        with open(output_file, 'w') as f:
            json.dump(list(unique_assets.values()), f, indent=2)
            
        return list(unique_assets.values())
        
    finally:
        driver.quit()

def compare_asset_lists(old_assets, new_assets):
    print("\n" + "="*80)
    print("ASSET COMPARISON RESULTS")
    print("="*80)
    
    # Create maps for easy lookup
    old_map = {a.get('name', 'Unknown'): a for a in old_assets if isinstance(a, dict)}
    new_map = {a.get('name', 'Unknown'): a for a in new_assets if isinstance(a, dict)}
    
    old_names = set(old_map.keys())
    new_names = set(new_map.keys())
    
    missing = old_names - new_names
    added = new_names - old_names
    common = old_names & new_names
    
    print(f"📊 Old Count: {len(old_names)}")
    print(f"📊 New Count: {len(new_names)}")
    print(f"❌ Missing Assets: {len(missing)}")
    print(f"➕ Added Assets: {len(added)}")
    
    if missing:
        print("\n🔴 MISSING ASSETS (Present in Old, Missing in New):")
        for name in sorted(missing):
            print(f"  - {name}")
            
    if added:
        print("\n🟢 ADDED ASSETS (New in New, Missing in Old):")
        for name in sorted(added):
            print(f"  + {name}")
            
    # Check details of common assets
    print("\n🔍 Checking details of common assets...")
    diffs = 0
    for name in common:
        old = old_map[name]
        new = new_map[name]
        
        # Compare specific fields
        fields_to_check = ['status', 'type', 'model', 'serial_number', 'location']
        for field in fields_to_check:
            v1 = old.get(field)
            v2 = new.get(field)
            if v1 != v2 and v1 and v2:
                print(f"  ⚠️  {name}: {field} changed '{v1}' -> '{v2}'")
                diffs += 1
                
    if diffs == 0:
        print("  ✅ No detail differences found in common assets")

def main():
    print("DEEP ASSET COMPARISON TOOL")
    print("This tool will compare the actual LIST of assets (names, details).")
    
    # 1. Capture Old
    print("\nSTEP 1: Capture RND (Old) Assets")
    old_assets = capture_assets("https://acme.egalvanic-rnd.com", "Super Caremark", "rnd_assets")
    
    # 2. Capture New
    print("\nSTEP 2: Capture AI (New) Assets")
    new_assets = capture_assets("https://acme.egalvanic.ai", "Super Caremark", "ai_assets")
    
    # 3. Compare
    compare_asset_lists(old_assets, new_assets)

if __name__ == "__main__":
    main()
