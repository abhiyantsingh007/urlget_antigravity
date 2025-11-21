import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_correct_login():
    """Test login with the correct credentials"""
    
    # Configuration with correct credentials
    BASE_URL = "https://acme.qa.egalvanic.ai"
    EMAIL = "rahul+acme@egalvanic.com"  # Corrected email
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
        print("=== LOGIN WITH CORRECT CREDENTIALS ===")
        print(f"URL: {BASE_URL}/login")
        print(f"Email: {EMAIL}")
        print(f"Password: {PASSWORD}")
        print("=" * 40)
        
        print("Navigating to login page...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)
        
        # Save screenshot of login page
        driver.save_screenshot("correct_login_page.png")
        print("Login page screenshot saved as correct_login_page.png")
        
        # Find and fill email field
        try:
            email_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.send_keys(EMAIL)
            print("✓ Email entered")
        except Exception as e:
            print(f"✗ Error entering email: {str(e)}")
            return False
        
        # Find and fill password field
        try:
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(PASSWORD)
            print("✓ Password entered")
        except Exception as e:
            print(f"✗ Error entering password: {str(e)}")
            return False
        
        # Find and click submit button
        try:
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            print("✓ Submit button clicked")
        except:
            # Try alternative selectors
            try:
                submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
                submit_button.click()
                print("✓ Submit button clicked (contains Login)")
            except Exception as e:
                print(f"✗ Error clicking submit button: {str(e)}")
                return False
        
        # Wait for response and check result
        print("Waiting for login response...")
        time.sleep(5)
        
        after_login_url = driver.current_url
        print(f"URL after login attempt: {after_login_url}")
        
        # Save screenshot after login attempt
        driver.save_screenshot("correct_after_login.png")
        print("After login screenshot saved as correct_after_login.png")
        
        # Check if login was successful
        if "dashboard" in after_login_url.lower() or "home" in after_login_url.lower():
            print("✓ LOGIN SUCCESSFUL!")
            print("✓ Successfully navigated to dashboard")
            return True
        elif "/login" in after_login_url:
            print("✗ LOGIN FAILED - Still on login page")
            return False
        else:
            print("? LOGIN STATUS UNCLEAR - Redirected to unexpected page")
            print(f"  Current page: {after_login_url}")
            return None
        
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        driver.save_screenshot("correct_login_error.png")
        print("Error screenshot saved as correct_login_error.png")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    result = test_correct_login()
    if result is True:
        print("\nRESULT: Login was successful with corrected credentials!")
    elif result is False:
        print("\nRESULT: Login failed even with corrected credentials")
    else:
        print("\nRESULT: Login status unclear with corrected credentials")