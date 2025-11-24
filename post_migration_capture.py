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

class PostMigrationDataCapture:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.driver = None
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"post_migration_capture_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "api_responses"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "page_sources"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "visible_texts"), exist_ok=True)
        
        print(f"Created output directory: {self.output_dir}")
    
    def setup_driver(self):
        """Setup Chrome driver with network logging enabled"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # Uncomment the line below to run in headless mode
        # chrome_options.add_argument("--headless")
        
        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Setup ChromeDriver automatically
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome driver initialized")
    
    def login(self):
        """Login to the ACME website"""
        print("Logging in to the website...")
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        # Enter credentials
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for dashboard to load
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )
        print("Login successful")
        time.sleep(3)
    
    def capture_all_pages_data(self):
        """Navigate to all pages and capture data"""
        print("Capturing data from all pages...")
        
        # Define all pages to visit
        pages = [
            {"name": "dashboard", "url": "/dashboard"},
            {"name": "sites", "url": "/sites"},
            {"name": "assets", "url": "/assets"},
            {"name": "issues", "url": "/issues"},
            {"name": "reports", "url": "/reports"},
            {"name": "settings", "url": "/settings"},
            {"name": "profile", "url": "/profile"}
        ]
        
        page_data = {}
        
        for i, page in enumerate(pages, 1):
            page_name = page["name"]
            page_url = page["url"]
            
            print(f"Processing {page_name} page ({i}/{len(pages)})...")
            
            # Navigate to page
            self.driver.get(f"{self.base_url}{page_url}")
            time.sleep(3)  # Wait for page to load
            
            # Take screenshot
            screenshot_path = os.path.join(self.output_dir, "screenshots", f"{page_name}.png")
            self.driver.save_screenshot(screenshot_path)
            
            # Save page source
            page_source_path = os.path.join(self.output_dir, "page_sources", f"{page_name}.html")
            with open(page_source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            # Save visible text
            visible_text_path = os.path.join(self.output_dir, "visible_texts", f"{page_name}.txt")
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                with open(visible_text_path, 'w', encoding='utf-8') as f:
                    f.write(body_text)
            except Exception as e:
                print(f"Warning: Could not extract visible text for {page_name}: {e}")
            
            page_data[page_name] = {
                "url": page_url,
                "screenshot": f"screenshots/{page_name}.png",
                "page_source": f"page_sources/{page_name}.html",
                "visible_text": f"visible_texts/{page_name}.txt"
            }
            
            # Try to interact with page elements to trigger API calls
            self.trigger_api_calls()
        
        return page_data
    
    def trigger_api_calls(self):
        """Click on interactive elements to trigger API calls"""
        try:
            # Find buttons and links that might trigger API calls
            interactive_elements = self.driver.find_elements(By.XPATH, 
                "//button[contains(@class, 'btn')] | //a[@href] | //input[@type='button']")
            
            # Click on a few elements to trigger API calls (limit to 3 to avoid excessive clicking)
            clicked = 0
            for element in interactive_elements[:3]:
                try:
                    # Skip navigation links to other pages
                    if element.tag_name == "a":
                        href = element.get_attribute("href")
                        if href and (href.startswith("http") and self.base_url not in href):
                            continue
                    
                    element.click()
                    time.sleep(1)
                    clicked += 1
                    
                    # Take a screenshot after clicking
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    click_screenshot = os.path.join(self.output_dir, "screenshots", f"click_{timestamp}.png")
                    self.driver.save_screenshot(click_screenshot)
                    
                except Exception as e:
                    pass  # Ignore errors when clicking elements
            
            if clicked > 0:
                print(f"  Triggered {clicked} API calls by clicking elements")
                time.sleep(2)  # Wait for API calls to complete
                
        except Exception as e:
            print(f"  Warning: Could not trigger API calls: {e}")
    
    def capture_api_responses(self):
        """Capture all API responses automatically from browser network logs"""
        print("Capturing API responses...")
        
        # Get performance logs
        logs = self.driver.get_log('performance')
        
        api_responses = []
        response_count = 0
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                
                # Check if this is a response received event
                if (message['message']['method'] == 'Network.responseReceived' and 
                    'response' in message['message']['params']):
                    
                    response = message['message']['params']['response']
                    url = response['url']
                    
                    # Filter for API endpoints (typically containing /api/ or returning JSON)
                    if (('/api/' in url or 'json' in response.get('mimeType', '')) and 
                        response['status'] == 200):
                        
                        try:
                            # Enable Network domain to get response bodies
                            self.driver.execute_cdp_cmd('Network.enable', {})
                            
                            # Get response body
                            request_id = message['message']['params']['requestId']
                            result = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            response_body = result.get('body', '')
                            
                            # Handle base64 encoded responses
                            if result.get('base64Encoded', False):
                                import base64
                                response_body = base64.b64decode(response_body).decode('utf-8')
                            
                            # Try to parse as JSON
                            try:
                                response_body = json.loads(response_body)
                            except:
                                pass  # Keep as string if not JSON
                            
                            # Create API response entry
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
                            filepath = os.path.join(self.output_dir, "api_responses", filename)
                            
                            with open(filepath, 'w') as f:
                                json.dump(api_entry, f, indent=2, default=str)
                            
                            print(f"  Saved API response: {filename}")
                            
                        except Exception as e:
                            print(f"  Warning: Could not get response body for {url}: {e}")
                            
            except Exception as e:
                continue  # Skip malformed log entries
        
        # Also save all responses in a single file
        all_responses_path = os.path.join(self.output_dir, "api_responses", "all_responses.json")
        with open(all_responses_path, 'w') as f:
            json.dump(api_responses, f, indent=2, default=str)
        
        print(f"Captured {len(api_responses)} API responses")
        return api_responses
    
    def run_capture(self):
        """Run the complete post-migration data capture"""
        try:
            print("=== STARTING POST-MIGRATION DATA CAPTURE ===")
            
            self.setup_driver()
            self.login()
            
            # Capture data from all pages
            page_data = self.capture_all_pages_data()
            
            # Capture API responses
            api_responses = self.capture_api_responses()
            
            # Create summary
            summary = {
                "capture_timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "pages_captured": list(page_data.keys()),
                "api_responses_captured": len(api_responses),
                "output_directory": self.output_dir
            }
            
            summary_path = os.path.join(self.output_dir, "capture_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print("\n=== POST-MIGRATION CAPTURE COMPLETED ===")
            print(f"Pages captured: {len(page_data)}")
            print(f"API responses captured: {len(api_responses)}")
            print(f"All data saved to: {self.output_dir}")
            
            return self.output_dir
            
        except Exception as e:
            print(f"Error during capture: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
            
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    # Configuration - Update with actual credentials
    BASE_URL = "https://acme.egalvanic.ai"  # Update if URL changes after migration
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Run post-migration capture
    capture = PostMigrationDataCapture(BASE_URL, EMAIL, PASSWORD)
    output_directory = capture.run_capture()
    
    print(f"\nPost-migration capture completed. Data saved to: {output_directory}")