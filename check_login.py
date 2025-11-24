import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def check_login():
    """Check if we can log in with the provided credentials"""
    
    # Configuration
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul@egalvanic.com"
    PASSWORD = "RP@egalvanic123"
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--headless")  # Run in headless mode
    
    # Setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("=== LOGIN CREDENTIALS CHECK ===")
        print(f"URL: {BASE_URL}/login")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
        print("=" * 40)
        
        print("Navigating to login page...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)
        
        # Check if we're on the login page
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Save screenshot of login page
        driver.save_screenshot("check_login_page.png")
        print("Login page screenshot saved as check_login_page.png")
        
        # Try to find email and password fields
        try:
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            print("✓ Email field found")
        except:
            print("✗ Email field not found")
            # Try alternative selectors
            try:
                email_field = driver.find_element(By.ID, "email")
                print("✓ Email field found (by ID)")
            except:
                print("✗ Email field not found (by ID)")
                try:
                    email_field = driver.find_element(By.XPATH, "//input[@type='email']")
                    print("✓ Email field found (by type)")
                except:
                    print("✗ Email field not found (by type)")
                    email_field = None
        
        try:
            password_field = driver.find_element(By.NAME, "password")
            print("✓ Password field found")
        except:
            print("✗ Password field not found")
            # Try alternative selectors
            try:
                password_field = driver.find_element(By.ID, "password")
                print("✓ Password field found (by ID)")
            except:
                print("✗ Password field not found (by ID)")
                try:
                    password_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
                    if password_fields:
                        password_field = password_fields[0]
                        print("✓ Password field found (by type)")
                    else:
                        print("✗ Password field not found (by type)")
                        password_field = None
                except:
                    print("✗ Password field not found (by type)")
                    password_field = None
        
        # Enter credentials if fields are found
        if email_field:
            email_field.send_keys(EMAIL)
            print("✓ Email entered")
        else:
            print("✗ Could not enter email")
        
        if password_field:
            password_field.send_keys(PASSWORD)
            print("✓ Password entered")
        else:
            print("✗ Could not enter password")
        
        # Try to find and click submit button
        submit_found = False
        try:
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            submit_found = True
            print("✓ Submit button clicked")
        except:
            print("✗ Submit button not found (type=submit)")
            # Try alternative selectors
            try:
                submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
                submit_button.click()
                submit_found = True
                print("✓ Submit button clicked (contains Login)")
            except:
                print("✗ Submit button not found (contains Login)")
                try:
                    submit_buttons = driver.find_elements(By.XPATH, "//input[@type='submit']")
                    if submit_buttons:
                        submit_buttons[0].click()
                        submit_found = True
                        print("✓ Submit button clicked (input type=submit)")
                    else:
                        print("✗ Submit button not found (input type=submit)")
                except:
                    print("✗ Submit button not found (input type=submit)")
        
        # Wait and check result
        time.sleep(5)
        after_login_url = driver.current_url
        print(f"URL after login attempt: {after_login_url}")
        
        # Save screenshot after login attempt
        driver.save_screenshot("check_after_login.png")
        print("After login screenshot saved as check_after_login.png")
        
        # Check if login was successful
        if "dashboard" in after_login_url.lower() or "home" in after_login_url.lower():
            print("✓ LOGIN SUCCESSFUL!")
            return True
        elif after_login_url == current_url:
            print("✗ LOGIN FAILED - Still on login page")
            return False
        else:
            print("? LOGIN STATUS UNKNOWN - Redirected to different page")
            print("  This might indicate success or failure")
            return None
        
    except Exception as e:
        print(f"Error during login check: {str(e)}")
        driver.save_screenshot("check_error.png")
        print("Error screenshot saved as check_error.png")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    result = check_login()
    if result is True:
        print("\nRESULT: Login was successful")
    elif result is False:
        print("\nRESULT: Login failed")
    else:
        print("\nRESULT: Login status unclear")