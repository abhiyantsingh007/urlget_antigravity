import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class EnhancedSiteDataCapture:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.driver = None
        
        # Create timestamped output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"enhanced_site_capture_{timestamp}"
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
        # Run in headless mode to avoid display issues
        chrome_options.add_argument("--headless")
        
        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome driver initialized successfully")
    
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
    
    def get_all_sites_from_dropdown(self):
        """Get all sites from the site dropdown"""
        print("Getting all sites from dropdown...")
        
        # Navigate to sites page or wherever the dropdown is accessible
        self.driver.get(f"{self.base_url}/sites")
        time.sleep(3)
        
        try:
            # Find the site dropdown - adjust selector based on actual website
            # This is a common pattern, but you may need to adjust the selector
            site_dropdown = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='site'], select[id*='site'], .site-dropdown, [class*='site'][class*='dropdown']"))
            )
            
            # Create a Select object if it's a standard select element
            if site_dropdown.tag_name == "select":
                select = Select(site_dropdown)
                options = select.options
                sites = [option.text.strip() for option in options if option.text.strip()]
            else:
                # If it's a custom dropdown, we need to click it to reveal options
                site_dropdown.click()
                time.sleep(1)
                
                # Find all option elements - adjust selector based on actual website
                option_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".dropdown-menu li, .site-option, [data-site], [role='option']")
                sites = []
                for element in option_elements:
                    text = element.text.strip()
                    if text and text not in sites:
                        sites.append(text)
                
                # Click the dropdown again to close it
                site_dropdown.click()
            
            print(f"Found {len(sites)} sites in dropdown: {sites}")
            return sites
            
        except Exception as e:
            print(f"Warning: Could not identify site dropdown: {e}")
            print("Falling back to manual site list...")
            # Fallback to known sites from your description
            sites = ["London UK", "All Facilities", "Melbourne AU", "ShowSite3", "test", "test site", "Toronto Canada"]
            print(f"Using fallback site list: {sites}")
            return sites
    
    def select_site_and_capture_data(self, site_name):
        """Select a site from dropdown and capture all relevant data"""
        print(f"\n--- Capturing data for site: {site_name} ---")
        
        try:
            # Navigate to sites page
            self.driver.get(f"{self.base_url}/sites")
            time.sleep(3)
            
            # Select the site from dropdown
            # Adjust these selectors based on the actual website structure
            try:
                # Try standard select element first
                site_dropdown = self.driver.find_element(By.CSS_SELECTOR, 
                    "select[name='site'], select[id*='site'], .site-dropdown select")
                select = Select(site_dropdown)
                select.select_by_visible_text(site_name)
            except:
                # Try custom dropdown
                try:
                    # Click dropdown to open
                    dropdown_trigger = self.driver.find_element(By.CSS_SELECTOR,
                        ".site-dropdown, .dropdown-toggle, [data-toggle='dropdown']")
                    dropdown_trigger.click()
                    time.sleep(1)
                    
                    # Find and click the specific site option
                    site_option = self.driver.find_element(By.XPATH,
                        f"//li[contains(text(), '{site_name}') or @data-site='{site_name}']")
                    site_option.click()
                except:
                    print(f"Warning: Could not select site '{site_name}' from dropdown")
                    return False
            
            # Wait for page to update after site selection
            time.sleep(3)
            
            # Capture data for this site
            site_dir = os.path.join(self.output_dir, "sites", site_name.replace("/", "_").replace("\\", "_"))
            os.makedirs(site_dir, exist_ok=True)
            os.makedirs(os.path.join(site_dir, "api_responses"), exist_ok=True)
            os.makedirs(os.path.join(site_dir, "screenshots"), exist_ok=True)
            
            # Take screenshot
            screenshot_path = os.path.join(site_dir, "screenshots", f"{site_name.replace(' ', '_')}_overview.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"  ✓ Screenshot saved: {os.path.basename(screenshot_path)}")
            
            # Save page source
            page_source_path = os.path.join(site_dir, "page_source.html")
            with open(page_source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"  ✓ Page source saved: page_source.html")
            
            # Extract visible text
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                text_path = os.path.join(site_dir, "visible_text.txt")
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(body_text)
                print(f"  ✓ Visible text saved: visible_text.txt")
            except Exception as e:
                print(f"  ✗ Error extracting visible text: {e}")
            
            # Navigate to related pages for this site and capture data
            site_pages = [
                {"name": "assets", "url": "/assets"},
                {"name": "arc_flash", "url": "/arc-flash"},
                {"name": "resolved_issues", "url": "/issues/resolved"},
                {"name": "reports", "url": "/reports"}
            ]
            
            for page in site_pages:
                try:
                    page_name = page["name"]
                    page_url = page["url"]
                    
                    print(f"  Accessing {page_name} for {site_name}...")
                    self.driver.get(f"{self.base_url}{page_url}")
                    time.sleep(2)
                    
                    # Take screenshot
                    page_screenshot = os.path.join(site_dir, "screenshots", f"{page_name}.png")
                    self.driver.save_screenshot(page_screenshot)
                    print(f"    ✓ Screenshot saved: {page_name}.png")
                    
                    # Save page source
                    page_source_file = os.path.join(site_dir, f"{page_name}_source.html")
                    with open(page_source_file, 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print(f"    ✓ Page source saved: {page_name}_source.html")
                    
                except Exception as e:
                    print(f"    ✗ Error accessing {page_name}: {e}")
            
            print(f"  Completed data capture for site: {site_name}")
            return True
            
        except Exception as e:
            print(f"  Error capturing data for site '{site_name}': {e}")
            return False
    
    def capture_network_logs(self, site_name):
        """Capture network logs (API responses) for a specific site"""
        print(f"Capturing API responses for site: {site_name}...")
        
        try:
            # Get performance logs
            logs = self.driver.get_log('performance')
            
            api_responses = []
            response_count = 0
            
            site_dir = os.path.join(self.output_dir, "sites", site_name.replace("/", "_").replace("\\", "_"))
            api_dir = os.path.join(site_dir, "api_responses")
            os.makedirs(api_dir, exist_ok=True)
            
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
                                    'response': response_body,
                                    'site': site_name
                                }
                                
                                api_responses.append(api_entry)
                                response_count += 1
                                
                                # Save individual response to file
                                filename = f"response_{response_count}.json"
                                filepath = os.path.join(api_dir, filename)
                                
                                with open(filepath, 'w') as f:
                                    json.dump(api_entry, f, indent=2, default=str)
                                
                                print(f"  ✓ API response saved: {filename}")
                                
                            except Exception as e:
                                print(f"  ✗ Could not get response body for {url}: {e}")
                                
                except Exception as e:
                    continue  # Skip malformed log entries
            
            print(f"Captured {len(api_responses)} API responses for site: {site_name}")
            return api_responses
            
        except Exception as e:
            print(f"Error capturing network logs for site '{site_name}': {e}")
            return []
    
    def run_capture(self):
        """Run the complete enhanced site data capture"""
        try:
            print("=== STARTING ENHANCED SITE DATA CAPTURE ===")
            
            self.setup_driver()
            self.login()
            
            # Get all sites from dropdown
            sites = self.get_all_sites_from_dropdown()
            
            # Capture data for each site
            captured_sites = []
            total_api_responses = 0
            
            for site in sites:
                if self.select_site_and_capture_data(site):
                    captured_sites.append(site)
                    # Capture API responses for this site
                    api_responses = self.capture_network_logs(site)
                    total_api_responses += len(api_responses)
            
            # Create summary
            summary = {
                "capture_timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "sites_captured": captured_sites,
                "total_sites": len(captured_sites),
                "total_api_responses": total_api_responses,
                "output_directory": self.output_dir
            }
            
            summary_path = os.path.join(self.output_dir, "capture_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"\n=== ENHANCED SITE CAPTURE COMPLETED ===")
            print(f"Sites captured: {len(captured_sites)}")
            print(f"Total API responses captured: {total_api_responses}")
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

def run_enhanced_capture():
    """Run the enhanced site capture with default credentials"""
    # Configuration - Update with actual credentials
    BASE_URL = "https://acme.egalvanic.ai"
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Run enhanced capture
    capture = EnhancedSiteDataCapture(BASE_URL, EMAIL, PASSWORD)
    output_directory = capture.run_capture()
    
    print(f"\nEnhanced capture completed!")
    print(f"All data has been saved to: {output_directory}")
    print("\nDirectory structure:")
    print(f"{output_directory}/")
    print("├── capture_summary.json")
    print("└── sites/")
    for site in ["London UK", "All Facilities", "Melbourne AU", "ShowSite3", "test", "test site", "Toronto Canada"]:
        print(f"    └── {site}/")
        print(f"        ├── api_responses/")
        print(f"        ├── screenshots/")
        print(f"        ├── page_source.html")
        print(f"        └── visible_text.txt")

if __name__ == "__main__":
    run_enhanced_capture()