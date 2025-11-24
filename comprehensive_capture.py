import json
import os
import time
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class ComprehensiveCapture:
    def __init__(self, base_url, email, password, headless=True):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.driver = None
        self.headless = headless
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"comprehensive_capture_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "sites"), exist_ok=True)
        
        print(f"Created output directory: {self.output_dir}")
    
    def setup_driver(self):
        """Setup Chrome driver with network logging enabled"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome driver initialized successfully")
    
    def login(self):
        """Login to the ACME website"""
        print(f"Logging in to {self.base_url}...")
        self.driver.get(f"{self.base_url}/login")
        time.sleep(2)
        
        try:
            # Enter credentials
            self.driver.find_element(By.NAME, "email").send_keys(self.email)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            
            # Click submit
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            
            # Wait for dashboard
            WebDriverWait(self.driver, 15).until(
                EC.url_contains("/dashboard")
            )
            print("Login successful")
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False
            
    def get_all_sites(self):
        """Get all sites from the dropdown"""
        print("Getting all sites from dropdown...")
        self.driver.get(f"{self.base_url}/sites")
        time.sleep(3)
        
        sites = []
        try:
            # Try to find the dropdown
            # Strategy 1: Standard Select
            try:
                select_elem = self.driver.find_element(By.CSS_SELECTOR, "select[name='site'], select.site-select")
                select = Select(select_elem)
                sites = [opt.text.strip() for opt in select.options if opt.text.strip()]
            except:
                # Strategy 2: Custom Dropdown (Click to open, then find items)
                dropdown = self.driver.find_element(By.CSS_SELECTOR, ".site-dropdown, .dropdown-toggle")
                dropdown.click()
                time.sleep(1)
                items = self.driver.find_elements(By.CSS_SELECTOR, ".dropdown-menu li, .dropdown-item")
                sites = [item.text.strip() for item in items if item.text.strip()]
                # Close dropdown
                dropdown.click()
                
            print(f"Found {len(sites)} sites: {sites}")
            return sites
        except Exception as e:
            print(f"Error finding sites: {e}")
            # Fallback list
            return ["London UK", "All Facilities", "Melbourne AU", "ShowSite3", "test", "test site", "Toronto Canada", "Site657"]

    def capture_network_logs(self, site_name, output_path):
        """Capture network logs and save API responses"""
        logs = self.driver.get_log('performance')
        api_responses = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                if (message['message']['method'] == 'Network.responseReceived' and 
                    'response' in message['message']['params']):
                    
                    response = message['message']['params']['response']
                    url = response['url']
                    
                    # Filter for API calls
                    if ('/api/' in url or 'json' in response.get('mimeType', '')) and response['status'] == 200:
                        try:
                            # Get response body
                            request_id = message['message']['params']['requestId']
                            self.driver.execute_cdp_cmd('Network.enable', {})
                            result = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                            body = result.get('body', '')
                            
                            if result.get('base64Encoded', False):
                                import base64
                                body = base64.b64decode(body).decode('utf-8')
                                
                            try:
                                body = json.loads(body)
                            except:
                                pass
                                
                            api_entry = {
                                'url': url,
                                'status': response['status'],
                                'timestamp': log['timestamp'],
                                'response': body,
                                'site': site_name
                            }
                            api_responses.append(api_entry)
                        except Exception as e:
                            # Ignore errors getting body (sometimes request is gone)
                            pass
            except:
                continue
                
        # Save responses
        if api_responses:
            api_dir = os.path.join(output_path, "api_responses")
            os.makedirs(api_dir, exist_ok=True)
            for i, resp in enumerate(api_responses):
                with open(os.path.join(api_dir, f"response_{i}.json"), 'w') as f:
                    json.dump(resp, f, indent=2, default=str)
            print(f"  Saved {len(api_responses)} API responses")
            
        return len(api_responses)

    def capture_site_data(self, site_name):
        """Capture data for a specific site"""
        print(f"\n--- Capturing {site_name} ---")
        site_safe_name = site_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
        site_dir = os.path.join(self.output_dir, "sites", site_safe_name)
        os.makedirs(site_dir, exist_ok=True)
        
        try:
            # 1. Select Site
            # This part depends heavily on how the site selection works.
            # Assuming we can navigate to a URL or use the dropdown.
            # For now, let's assume we are on the sites page and can click.
            self.driver.get(f"{self.base_url}/sites")
            time.sleep(2)
            
            # Try to select the site
            try:
                # Try standard select
                select_elem = self.driver.find_element(By.CSS_SELECTOR, "select[name='site'], select.site-select")
                Select(select_elem).select_by_visible_text(site_name)
            except:
                # Try custom dropdown
                try:
                    dropdown = self.driver.find_element(By.CSS_SELECTOR, ".site-dropdown, .dropdown-toggle")
                    dropdown.click()
                    time.sleep(1)
                    # Find option by text
                    option = self.driver.find_element(By.XPATH, f"//li[contains(text(), '{site_name}')] | //a[contains(text(), '{site_name}')]")
                    option.click()
                except:
                    print(f"  Could not select site {site_name} via UI")
            
            time.sleep(3) # Wait for load
            
            # 2. Capture Dashboard
            self.driver.save_screenshot(os.path.join(site_dir, "dashboard.png"))
            with open(os.path.join(site_dir, "dashboard.html"), 'w') as f:
                f.write(self.driver.page_source)
                
            # 3. Capture Network Logs
            self.capture_network_logs(site_name, site_dir)
            
            # 4. Visit Assets Page (if exists)
            try:
                self.driver.get(f"{self.base_url}/assets")
                time.sleep(2)
                self.driver.save_screenshot(os.path.join(site_dir, "assets.png"))
                with open(os.path.join(site_dir, "assets.html"), 'w') as f:
                    f.write(self.driver.page_source)
                self.capture_network_logs(site_name, site_dir) # Capture assets API calls
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"  Error capturing {site_name}: {e}")
            return False

    def run(self):
        try:
            self.setup_driver()
            if self.login():
                sites = self.get_all_sites()
                for site in sites:
                    self.capture_site_data(site)
        finally:
            if self.driver:
                self.driver.quit()
        
        print(f"\nCapture complete. Data saved to {self.output_dir}")
        return self.output_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Comprehensive Data Capture')
    parser.add_argument('--url', required=True, help='Base URL of the website')
    parser.add_argument('--email', default="rahul+acme@egalvanic.com", help='Login email')
    parser.add_argument('--password', default="RP@egalvanic123", help='Login password')
    
    args = parser.parse_args()
    
    capture = ComprehensiveCapture(args.url, args.email, args.password)
    capture.run()
