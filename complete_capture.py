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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def capture_complete_data():
    """Capture complete data from the ACME website using Selenium"""
    
    # Configuration with correct credentials
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul+acme@egalvanic.com"  # Corrected email
    PASSWORD = "RP@egalvanic123"
    
    # Create output directory
    output_dir = "complete_captures_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Run in headless mode for faster execution
    chrome_options.add_argument("--headless")
    
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
        print("Starting complete data capture...")
        
        # Step 1: Navigate to login page
        print("Step 1: Navigating to login page...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)
        
        # Step 2: Attempt login
        print("Step 2: Attempting login...")
        try:
            # Find and fill email field
            email_fields = driver.find_elements(By.XPATH, "//input[@type='email' or @name='email' or @id='email']")
            if email_fields:
                email_fields[0].send_keys(EMAIL)
                print("Email field filled")
            else:
                print("Email field not found")
            
            # Find and fill password field
            password_fields = driver.find_elements(By.XPATH, "//input[@type='password' or @name='password' or @id='password']")
            if password_fields:
                password_fields[0].send_keys(PASSWORD)
                print("Password field filled")
            else:
                print("Password field not found")
            
            # Find and click submit button
            submit_buttons = driver.find_elements(By.XPATH, "//button[@type='submit' or contains(text(), 'Login')]")
            if submit_buttons:
                submit_buttons[0].click()
                print("Login button clicked")
            else:
                print("Submit button not found")
            
            # Wait a bit for login to process
            time.sleep(3)
            
        except Exception as e:
            print(f"Login attempt failed: {str(e)}")
        
        # Step 3: Wait for dashboard or check if login was successful
        print("Step 3: Checking login status...")
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Step 4: Navigate to key pages
        pages_to_visit = [
            "/dashboard",
            "/sites",
            "/profile"
        ]
        
        for i, page in enumerate(pages_to_visit):
            try:
                print(f"Step {5+i}: Visiting {page}...")
                driver.get(f"{BASE_URL}{page}")
                time.sleep(3)  # Wait for page to load
                
                # Take screenshot
                screenshot_name = f"screenshot_{i+1}_{page.replace('/', '')}.png"
                screenshot_path = os.path.join(output_dir, screenshot_name)
                driver.save_screenshot(screenshot_path)
                captured_data["screenshots"].append(screenshot_name)
                print(f"Screenshot saved: {screenshot_name}")
                
                # Capture page source
                page_source = driver.page_source
                source_file = f"page_source_{i+1}_{page.replace('/', '')}.html"
                source_path = os.path.join(output_dir, source_file)
                with open(source_path, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"Page source saved: {source_file}")
                
                # Try to extract any JSON data from the page
                try:
                    # Look for any script tags containing JSON data
                    script_elements = driver.find_elements(By.XPATH, "//script[@type='application/json' or contains(text(), '{')]")
                    for j, script in enumerate(script_elements):
                        script_content = script.get_attribute('innerHTML')
                        if script_content and len(script_content) > 50:  # Only if it's substantial
                            try:
                                # Try to parse as JSON
                                json_data = json.loads(script_content)
                                json_file = f"json_data_{i+1}_{j+1}.json"
                                json_path = os.path.join(output_dir, json_file)
                                with open(json_path, 'w') as f:
                                    json.dump(json_data, f, indent=2)
                                print(f"JSON data extracted: {json_file}")
                            except:
                                # Save as text if not valid JSON
                                text_file = f"text_data_{i+1}_{j+1}.txt"
                                text_path = os.path.join(output_dir, text_file)
                                with open(text_path, 'w', encoding='utf-8') as f:
                                    f.write(script_content)
                                print(f"Text data extracted: {text_file}")
                except Exception as e:
                    print(f"Error extracting JSON data: {str(e)}")
                    
            except Exception as e:
                print(f"Error visiting {page}: {str(e)}")
        
        # Step 5: Capture network logs (API responses)
        print("Step 8: Capturing network logs...")
        try:
            logs = driver.get_log('performance')
            api_response_count = 0
            
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
                                
                                print(f"API response saved: {filename}")
                                
                            except Exception as e:
                                print(f"Could not get response body for {url}: {str(e)}")
                                
                except Exception as e:
                    continue  # Skip malformed log entries
            
            print(f"Captured {api_response_count} API responses")
            
        except Exception as e:
            print(f"Error capturing network logs: {str(e)}")
        
        # Step 6: Extract visible text content
        print("Step 9: Extracting visible text content...")
        try:
            body_element = driver.find_element(By.TAG_NAME, "body")
            visible_text = body_element.text
            captured_data["ui_data"]["visible_text"] = visible_text
            
            # Save visible text to file
            text_file = os.path.join(output_dir, "visible_text.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(visible_text)
            print(f"Visible text saved: visible_text.txt")
            
            # Extract page title
            captured_data["ui_data"]["page_title"] = driver.title
            print(f"Page title: {driver.title}")
            
        except Exception as e:
            print(f"Error extracting visible text: {str(e)}")
        
        # Step 7: Save all captured data
        print("Step 10: Saving all captured data...")
        all_data_file = os.path.join(output_dir, "complete_capture.json")
        with open(all_data_file, 'w') as f:
            json.dump(captured_data, f, indent=2, default=str)
        
        # Create summary
        summary = {
            "capture_timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "pages_visited": pages_to_visit,
            "api_responses_captured": len(captured_data["api_responses"]),
            "screenshots_taken": len(captured_data["screenshots"]),
            "output_directory": output_dir
        }
        
        summary_file = os.path.join(output_dir, "capture_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nComplete capture finished successfully!")
        print(f"API responses captured: {len(captured_data['api_responses'])}")
        print(f"Screenshots taken: {len(captured_data['screenshots'])}")
        print(f"Data saved to: {output_dir}")
        
        return output_dir
        
    except Exception as e:
        print(f"Error during complete capture: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_complete_data()