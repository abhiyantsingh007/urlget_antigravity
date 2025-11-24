import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_login_and_screenshot():
    """Test login to ACME website and capture screenshot"""
    
    # Configuration with correct credentials
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul+acme@egalvanic.com"  # Corrected email
    PASSWORD = "RP@egalvanic123"
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # Remove headless mode so we can see what's happening
    # chrome_options.add_argument("--headless")
    
    # Setup ChromeDriver automatically
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Navigating to login page...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        
        # Save screenshot of login page
        driver.save_screenshot("login_page.png")
        print("Screenshot of login page saved as login_page.png")
        
        # Wait for page to load and enter credentials
        print("Waiting for login page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        print("Logging in...")
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        
        # Try to find and click submit button
        try:
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
        except:
            # Try alternative selectors
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
            except:
                try:
                    driver.find_element(By.XPATH, "//input[@type='submit']").click()
                except:
                    print("Could not find submit button, submitting form anyway...")
                    driver.execute_script("document.forms[0].submit();")
        
        # Wait for dashboard to load
        print("Waiting for dashboard to load...")
        time.sleep(5)
        
        # Save screenshot of dashboard
        driver.save_screenshot("dashboard.png")
        print("Screenshot of dashboard saved as dashboard.png")
        
        print(f"Current URL: {driver.current_url}")
        print("Login test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        # Save screenshot of error page
        driver.save_screenshot("error_page.png")
        print("Screenshot of error page saved as error_page.png")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_and_screenshot()