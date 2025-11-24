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
from selenium.common.exceptions import TimeoutException

def capture_api_responses():
    """Capture all API responses from the ACME website"""
    
    # Configuration
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Create output directory
    output_dir = "api_captures_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Setup Chrome driver with network logging
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Add headless mode for faster execution
    chrome_options.add_argument("--headless")
    
    # Enable performance logging
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # Setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to login page...")
        driver.get(f"{BASE_URL}/login")
        
        # Wait for page to load and enter credentials (with timeout)
        print("Waiting for login page to load...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
        except TimeoutException:
            print("Login page took too long to load, continuing anyway...")
        
        print("Logging in...")
        try:
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.send_keys(EMAIL)
        except TimeoutException:
            # Try alternative selector
            try:
                driver.find_element(By.ID, "email").send_keys(EMAIL)
            except:
                print("Could not find email field, trying to fill anyway...")
                try:
                    driver.find_element(By.XPATH, "//input[@type='email']").send_keys(EMAIL)
                except:
                    pass
        
        try:
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(PASSWORD)
        except:
            # Try alternative selector
            try:
                driver.find_element(By.ID, "password").send_keys(PASSWORD)
            except:
                print("Could not find password field, trying to fill anyway...")
                try:
                    driver.find_elements(By.XPATH, "//input[@type='password']")[0].send_keys(PASSWORD)
                except:
                    pass
        
        # Try to find and click submit button
        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            submit_button.click()
        except TimeoutException:
            # Try alternative selectors
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
            except:
                try:
                    driver.find_element(By.XPATH, "//input[@type='submit']").click()
                except:
                    print("Could not find submit button, submitting form anyway...")
                    try:
                        driver.execute_script("document.forms[0].submit();")
                    except:
                        pass
        
        # Wait for dashboard to load (with timeout)
        print("Waiting for dashboard to load...")
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains("/dashboard")
            )
            print("Login successful")
        except TimeoutException:
            print("Dashboard did not load within expected time, continuing anyway...")
            # Check if we're on a dashboard-like page
            if "dashboard" in driver.current_url.lower():
                print("Looks like we're on the dashboard")
            else:
                print(f"Current URL: {driver.current_url}")
        
        # Wait for page to fully load
        time.sleep(3)
        
        # Navigate to key pages to trigger API calls
        pages_to_visit = [
            "/dashboard",
            "/sites"
        ]
        
        for page in pages_to_visit:
            print(f"Visiting {page}...")
            try:
                driver.get(f"{BASE_URL}{page}")
                time.sleep(2)  # Wait for API calls to complete
            except Exception as e:
                print(f"Error visiting {page}: {str(e)}")
        
        # Capture network logs
        print("Capturing network logs...")
        logs = driver.get_log('performance')
        
        # Extract API responses
        api_responses = []
        response_count = 0
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                
                if (message['message']['method'] == 'Network.responseReceived' and 
                    'response' in message['message']['params']):
                    
                    response = message['message']['params']['response']
                    url = response['url']
                    
                    # Filter for API endpoints
                    if ('/api/' in url or 'json' in response.get('mimeType', '')) and response['status'] == 200:
                        # Get response body (requires enabling Network domain)
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
                            
                            api_responses.append(api_entry)
                            response_count += 1
                            
                            # Save individual response to file
                            filename = f"response_{response_count}.json"
                            filepath = os.path.join(output_dir, filename)
                            
                            with open(filepath, 'w') as f:
                                json.dump(api_entry, f, indent=2, default=str)
                            
                            print(f"Saved response from {url} to {filename}")
                            
                        except Exception as e:
                            print(f"Could not get response body for {url}: {str(e)}")
                            
            except Exception as e:
                continue  # Skip malformed log entries
        
        # Save all responses to a single file
        all_responses_file = os.path.join(output_dir, "all_responses.json")
        with open(all_responses_file, 'w') as f:
            json.dump(api_responses, f, indent=2, default=str)
        
        # Create summary
        summary = {
            "capture_timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "pages_visited": pages_to_visit,
            "responses_captured": response_count,
            "output_directory": output_dir
        }
        
        summary_file = os.path.join(output_dir, "capture_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nCapture completed successfully!")
        print(f"Total API responses captured: {response_count}")
        print(f"Data saved to: {output_dir}")
        print(f"\nTo compare after migration, simply run this script again and compare the JSON files.")
        
        return output_dir
        
    except Exception as e:
        print(f"Error during capture: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_api_responses()