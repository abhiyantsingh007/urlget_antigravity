import json
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests

class APIDataCapture:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.driver = None
        self.api_responses = {}
        self.session = requests.Session()
        
        # Create directories for storing data
        self.output_dir = "captured_data_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "api_responses"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "ui_data"), exist_ok=True)
    
    def setup_driver(self):
        """Setup Chrome driver with network logging enabled"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # Uncomment the line below to run in headless mode
        # chrome_options.add_argument("--headless")
        
        # Enable logging
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        # Automatically download and setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=caps)
        print("Chrome driver initialized")
    
    def login(self):
        """Login to the ACME website"""
        print("Navigating to login page...")
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        # Enter credentials
        print("Entering credentials...")
        email_input = self.driver.find_element(By.NAME, "email")
        password_input = self.driver.find_element(By.NAME, "password")
        
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        
        # Submit login form
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        print("Login successful")
        time.sleep(3)  # Wait for dashboard to fully load
    
    def capture_network_logs(self):
        """Capture network logs from browser"""
        print("Capturing network logs...")
        logs = self.driver.get_log('performance')
        
        api_calls = []
        for log in logs:
            message = json.loads(log['message'])
            if message['message']['method'] == 'Network.responseReceived':
                response = message['message']['params']['response']
                url = response['url']
                
                # Filter for API calls (you may need to adjust this based on the actual API structure)
                if '/api/' in url or 'json' in response.get('mimeType', ''):
                    api_calls.append({
                        'url': url,
                        'status': response['status'],
                        'headers': response['headers'],
                        'timestamp': log['timestamp']
                    })
        
        # Save API call metadata
        with open(os.path.join(self.output_dir, "api_calls_summary.json"), 'w') as f:
            json.dump(api_calls, f, indent=2)
            
        print(f"Captured {len(api_calls)} API calls")
        return api_calls
    
    def capture_api_responses(self):
        """Capture actual API responses by replaying requests"""
        print("Capturing API responses...")
        
        # Get current session cookies from selenium
        selenium_cookies = self.driver.get_cookies()
        for cookie in selenium_cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        
        # Example API endpoints (you'll need to adjust these based on the actual website)
        api_endpoints = [
            "/api/sites",
            "/api/users/profile",
            "/api/dashboard/stats",
            "/api/notifications",
            # Add more endpoints as needed
        ]
        
        captured_responses = {}
        
        for endpoint in api_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"Fetching {url}...")
                
                response = self.session.get(url)
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                
                # Save response to file
                filename = f"{endpoint.replace('/', '_').replace('api_', '')}.json"
                filepath = os.path.join(self.output_dir, "api_responses", filename)
                
                with open(filepath, 'w') as f:
                    if isinstance(response_data, (dict, list)):
                        json.dump(response_data, f, indent=2)
                    else:
                        f.write(response_data)
                
                captured_responses[endpoint] = {
                    'status_code': response.status_code,
                    'data': response_data,
                    'headers': dict(response.headers)
                }
                
                print(f"Saved response for {endpoint} to {filename}")
                
            except Exception as e:
                print(f"Error fetching {endpoint}: {str(e)}")
        
        self.api_responses = captured_responses
        return captured_responses
    
    def capture_ui_data(self):
        """Capture relevant UI data from the dashboard"""
        print("Capturing UI data...")
        ui_data = {}
        
        # Navigate to dashboard if not already there
        if "dashboard" not in self.driver.current_url:
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
        
        # Capture page title
        ui_data['page_title'] = self.driver.title
        
        # Capture visible text content
        ui_data['page_text'] = self.driver.find_element(By.TAG_NAME, "body").text
        
        # Capture specific elements (adjust selectors based on actual website)
        try:
            # Example: Capture navigation menu items
            nav_items = self.driver.find_elements(By.CSS_SELECTOR, "nav a, .navbar a")
            ui_data['navigation_items'] = [item.text for item in nav_items if item.text.strip()]
            
            # Example: Capture dashboard widgets/statistics
            stats = self.driver.find_elements(By.CSS_SELECTOR, ".stat-card, .dashboard-stat, .metric-box")
            ui_data['dashboard_stats'] = [stat.text for stat in stats if stat.text.strip()]
            
            # Example: Capture table data
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            table_data = []
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                table_rows = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        table_rows.append([cell.text for cell in cells])
                if table_rows:
                    table_data.append(table_rows)
            ui_data['tables'] = table_data
            
        except Exception as e:
            print(f"Error capturing UI elements: {str(e)}")
        
        # Save UI data to file
        filepath = os.path.join(self.output_dir, "ui_data", "dashboard_ui.json")
        with open(filepath, 'w') as f:
            json.dump(ui_data, f, indent=2)
            
        print(f"Saved UI data to {filepath}")
        return ui_data
    
    def capture_screenshots(self):
        """Capture screenshots of key pages"""
        print("Capturing screenshots...")
        
        screenshot_dir = os.path.join(self.output_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Take screenshot of dashboard
        self.driver.save_screenshot(os.path.join(screenshot_dir, "dashboard.png"))
        
        # Navigate to and capture other key pages
        pages = [
            ("/sites", "sites"),
            ("/profile", "profile"),
            ("/settings", "settings")
        ]
        
        for url_path, name in pages:
            try:
                self.driver.get(f"{self.base_url}{url_path}")
                time.sleep(2)  # Wait for page to load
                self.driver.save_screenshot(os.path.join(screenshot_dir, f"{name}.png"))
                print(f"Captured screenshot for {name}")
            except Exception as e:
                print(f"Error capturing screenshot for {name}: {str(e)}")
        
        print("Screenshots captured")
    
    def run_capture(self):
        """Run the complete data capture process"""
        try:
            print("Starting data capture process...")
            
            self.setup_driver()
            self.login()
            
            # Capture all data
            self.capture_network_logs()
            api_responses = self.capture_api_responses()
            ui_data = self.capture_ui_data()
            self.capture_screenshots()
            
            # Create summary report
            summary = {
                "capture_timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "output_directory": self.output_dir,
                "api_endpoints_captured": len(api_responses),
                "ui_elements_captured": len(ui_data) if isinstance(ui_data, dict) else 0
            }
            
            with open(os.path.join(self.output_dir, "capture_summary.json"), 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"\nData capture completed successfully!")
            print(f"All data saved to: {self.output_dir}")
            print(f"API responses: {len(api_responses)} endpoints")
            
            return summary
            
        except Exception as e:
            print(f"Error during data capture: {str(e)}")
            raise
            
        finally:
            if self.driver:
                self.driver.quit()

def compare_data(old_data_dir, new_data_dir):
    """Compare data between two capture sessions"""
    print(f"Comparing data between {old_data_dir} and {new_data_dir}")
    
    comparison_results = {}
    
    # Compare API responses
    old_api_dir = os.path.join(old_data_dir, "api_responses")
    new_api_dir = os.path.join(new_data_dir, "api_responses")
    
    if os.path.exists(old_api_dir) and os.path.exists(new_api_dir):
        old_files = set(os.listdir(old_api_dir))
        new_files = set(os.listdir(new_api_dir))
        
        comparison_results['api_files'] = {
            'added': list(new_files - old_files),
            'removed': list(old_files - new_files),
            'common': list(old_files & new_files)
        }
        
        # Compare content of common files
        for filename in comparison_results['api_files']['common']:
            try:
                with open(os.path.join(old_api_dir, filename), 'r') as f:
                    old_data = json.load(f)
                
                with open(os.path.join(new_api_dir, filename), 'r') as f:
                    new_data = json.load(f)
                
                if old_data != new_data:
                    comparison_results[f'api_{filename}_changed'] = True
                else:
                    comparison_results[f'api_{filename}_changed'] = False
                    
            except Exception as e:
                comparison_results[f'api_{filename}_comparison_error'] = str(e)
    
    # Save comparison results
    comparison_file = os.path.join(new_data_dir, "comparison_results.json")
    with open(comparison_file, 'w') as f:
        json.dump(comparison_results, f, indent=2)
    
    print(f"Comparison results saved to {comparison_file}")
    return comparison_results

if __name__ == "__main__":
    # Configuration
    BASE_URL = "https://acme.egalvanic.ai"
    EMAIL = "rahul@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Create and run data capture
    capture = APIDataCapture(BASE_URL, EMAIL, PASSWORD)
    summary = capture.run_capture()
    
    print("\nTo compare data after migration, run:")
    print(f"compare_data('path_to_old_capture', '{summary['output_directory']}')")
