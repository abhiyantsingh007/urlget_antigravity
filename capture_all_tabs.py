import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def capture_all_tabs_data():
    """Capture data from all tabs/pages of the ACME website"""
    
    # Configuration with correct credentials
    BASE_URL = "https://acme.egalvanic.ai"
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Create output directory
    output_dir = "complete_tab_captures_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Remove headless mode so we can see what's happening
    # chrome_options.add_argument("--headless")
    
    # Enable performance logging
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    captured_data = {
        "metadata": {
            "capture_timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "output_directory": output_dir
        },
        "api_responses": [],
        "ui_data": {},
        "screenshots": []
    }
    
    try:
        print("=== STARTING COMPREHENSIVE TAB DATA CAPTURE ===")
        
        # Step 1: Login
        print("Step 1: Logging in...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)
        
        # Enter credentials
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        print("✓ Login successful")
        time.sleep(3)
        
        # Step 2: Navigate to each tab/page and capture data
        tabs_to_visit = [
            {"name": "dashboard", "url": "/dashboard", "description": "Main dashboard with overview"},
            {"name": "sites", "url": "/sites", "description": "Sites management"},
            {"name": "assets", "url": "/assets", "description": "Assets management"},
            {"name": "issues", "url": "/issues", "description": "Issues tracking"},
            {"name": "reports", "url": "/reports", "description": "Reports and analytics"},
            {"name": "settings", "url": "/settings", "description": "System settings"},
            {"name": "profile", "url": "/profile", "description": "User profile"}
        ]
        
        api_response_count = 0
        
        for i, tab in enumerate(tabs_to_visit):
            tab_name = tab["name"]
            tab_url = tab["url"]
            tab_description = tab["description"]
            
            print(f"\nStep {i+2}: Capturing data from {tab_name} tab...")
            print(f"  URL: {BASE_URL}{tab_url}")
            print(f"  Description: {tab_description}")
            
            # Navigate to the tab
            driver.get(f"{BASE_URL}{tab_url}")
            time.sleep(4)  # Wait for page to load and API calls to complete
            
            # Take screenshot
            screenshot_name = f"screenshot_{i+1}_{tab_name}.png"
            screenshot_path = os.path.join(output_dir, screenshot_name)
            driver.save_screenshot(screenshot_path)
            captured_data["screenshots"].append(screenshot_name)
            print(f"  ✓ Screenshot saved: {screenshot_name}")
            
            # Save page source
            page_source = driver.page_source
            source_file = f"page_source_{i+1}_{tab_name}.html"
            source_path = os.path.join(output_dir, source_file)
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            print(f"  ✓ Page source saved: {source_file}")
            
            # Extract visible text
            try:
                body_element = driver.find_element(By.TAG_NAME, "body")
                visible_text = body_element.text
                text_file = f"visible_text_{i+1}_{tab_name}.txt"
                text_path = os.path.join(output_dir, text_file)
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(visible_text)
                print(f"  ✓ Visible text saved: {text_file}")
            except Exception as e:
                print(f"  ✗ Error extracting visible text: {str(e)}")
            
            # Try to click on any interactive elements to trigger more API calls
            try:
                # Look for buttons, links, or other interactive elements
                interactive_elements = driver.find_elements(By.XPATH, "//button | //a[@href] | //input[@type='button'] | //input[@type='submit']")
                clicked_elements = 0
                
                for element in interactive_elements[:5]:  # Limit to first 5 elements to avoid excessive clicking
                    try:
                        # Skip navigation links to avoid leaving the current page
                        if element.tag_name == "a" and element.get_attribute("href"):
                            href = element.get_attribute("href")
                            if href and BASE_URL in href and tab_url in href:
                                # This is a link within the same section, safe to click
                                pass
                            elif href and (href.startswith("#") or href.startswith("javascript:")):
                                # This is a local anchor or JavaScript link
                                pass
                            else:
                                # This is a navigation link, skip it
                                continue
                        
                        # Click the element
                        element.click()
                        time.sleep(1)
                        clicked_elements += 1
                        
                        # Take screenshot after clicking
                        click_screenshot = f"screenshot_{i+1}_{tab_name}_click_{clicked_elements}.png"
                        click_screenshot_path = os.path.join(output_dir, click_screenshot)
                        driver.save_screenshot(click_screenshot_path)
                        captured_data["screenshots"].append(click_screenshot)
                        print(f"  ✓ Clicked element and saved screenshot: {click_screenshot}")
                        
                    except Exception as e:
                        # Ignore errors from clicking elements
                        pass
                
                if clicked_elements > 0:
                    print(f"  ✓ Clicked {clicked_elements} interactive elements")
                    # Wait a bit more for any API calls triggered by clicks
                    time.sleep(2)
                    
            except Exception as e:
                print(f"  ✗ Error clicking interactive elements: {str(e)}")
        
        # Step 3: Capture network logs (API responses)
        print(f"\nStep {len(tabs_to_visit)+2}: Capturing network logs...")
        logs = driver.get_log('performance')
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                
                if (message['message']['method'] == 'Network.responseReceived' and 
                    'response' in message['message']['params']):
                    
                    response = message['message']['params']['response']
                    url = response['url']
                    
                    # Filter for API endpoints
                    if ('/api/' in url.lower() or 'json' in response.get('mimeType', '').lower()) and response['status'] == 200:
                        try:
                            # Enable Network domain to get response bodies
                            driver.execute_cdp_cmd('Network.enable', {})
                            
                            # Get response body
                            result = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': message['message']['params']['requestId']})
                            response_body = result.get('body', '')
                            
                            # Parse JSON if possible
                            try:
                                if result.get('base64Encoded', False):
                                    import base64
                                    response_body = base64.b64decode(response_body).decode('utf-8')
                                
                                parsed_body = json.loads(response_body)
                                response_body = parsed_body
                            except:
                                pass  # Keep as string if not JSON
                            
                            api_entry = {
                                'url': url,
                                'status': response['status'],
                                'mimeType': response.get('mimeType', ''),
                                'timestamp': log['timestamp'],
                                'response': response_body
                            }
                            
                            captured_data["api_responses"].append(api_entry)
                            api_response_count += 1
                            
                            # Save individual response to file
                            filename = f"api_response_{api_response_count}.json"
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'w') as f:
                                json.dump(api_entry, f, indent=2, default=str)
                            
                            print(f"  ✓ API response saved: {filename}")
                            
                        except Exception as e:
                            print(f"  ✗ Could not get response body for {url}: {str(e)}")
                            
            except Exception as e:
                continue  # Skip malformed log entries
        
        print(f"\nStep {len(tabs_to_visit)+3}: Finalizing capture...")
        
        # Save all captured data
        all_data_file = os.path.join(output_dir, "complete_tab_capture.json")
        with open(all_data_file, 'w') as f:
            json.dump(captured_data, f, indent=2, default=str)
        
        # Create summary
        summary = {
            "capture_timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "tabs_visited": [tab["name"] for tab in tabs_to_visit],
            "api_responses_captured": len(captured_data["api_responses"]),
            "screenshots_taken": len(captured_data["screenshots"]),
            "output_directory": output_dir
        }
        
        summary_file = os.path.join(output_dir, "capture_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n=== CAPTURE COMPLETED SUCCESSFULLY ===")
        print(f"Tabs visited: {len(tabs_to_visit)}")
        print(f"API responses captured: {len(captured_data['api_responses'])}")
        print(f"Screenshots taken: {len(captured_data['screenshots'])}")
        print(f"Data saved to: {output_dir}")
        
        return output_dir
        
    except Exception as e:
        print(f"Error during capture: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_all_tabs_data()