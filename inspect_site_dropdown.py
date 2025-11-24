#!/usr/bin/env python3
"""
Inspect the site dropdown to understand its structure
Takes screenshots and dumps HTML to help us figure out the correct selectors
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def inspect_dropdown():
    BASE_URL = "https://acme.egalvanic-rnd.com"
    EMAIL = "rahul+acme@egalvanic.com"
    PASSWORD = "RP@egalvanic123"

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # NOT headless so we can see what's happening

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print("🔐 Logging in...")
        driver.get(f"{BASE_URL}/login")
        time.sleep(2)

        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 15).until(EC.url_contains("/dashboard"))
        print("✅ Logged in successfully")
        time.sleep(3)

        # Take screenshot of dashboard
        driver.save_screenshot("dashboard_screenshot.png")
        print("📸 Screenshot saved: dashboard_screenshot.png")

        # Save page HTML
        with open("dashboard_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 HTML saved: dashboard_page_source.html")

        # Try to find all potential dropdown elements
        print("\n🔍 Looking for dropdown elements...")

        # Check for various dropdown patterns
        selectors = {
            "select tags": "select",
            "buttons with aria-label": "button[aria-label]",
            "role=button": "[role='button']",
            "role=combobox": "[role='combobox']",
            "autocomplete inputs": "input[role='combobox']",
            "mui-select": ".MuiSelect-root, [class*='Select']",
            "dropdown divs": "[class*='dropdown'], [class*='Dropdown']"
        }

        for name, selector in selectors.items():
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n✅ Found {len(elements)} '{name}' elements:")
                    for i, elem in enumerate(elements[:5]):  # Show first 5
                        try:
                            text = elem.text[:50] if elem.text else "(no text)"
                            aria_label = elem.get_attribute("aria-label") or "(no aria-label)"
                            class_name = elem.get_attribute("class") or "(no class)"
                            print(f"   [{i}] Text: {text}, Aria: {aria_label}, Class: {class_name[:50]}")
                        except:
                            pass
            except:
                pass

        # Try clicking on potential site selector
        print("\n\n🖱️  Attempting to click potential site dropdowns...")

        # Strategy 1: Look for autocomplete/combobox
        try:
            combos = driver.find_elements(By.CSS_SELECTOR, "[role='combobox'], input[role='combobox']")
            if combos:
                print(f"\nFound {len(combos)} combobox elements")
                for i, combo in enumerate(combos[:3]):
                    try:
                        print(f"  Combobox {i}: {combo.get_attribute('outerHTML')[:200]}")
                    except:
                        pass
        except Exception as e:
            print(f"  Error with combobox: {e}")

        # Strategy 2: Look for MUI Autocomplete
        try:
            mui_elements = driver.find_elements(By.CSS_SELECTOR, ".MuiAutocomplete-root, [class*='Autocomplete']")
            if mui_elements:
                print(f"\nFound {len(mui_elements)} MUI Autocomplete elements")
                for elem in mui_elements:
                    try:
                        # Find the input inside
                        input_elem = elem.find_element(By.CSS_SELECTOR, "input")
                        print(f"  MUI Input: {input_elem.get_attribute('outerHTML')[:200]}")

                        # Try clicking it
                        input_elem.click()
                        time.sleep(2)
                        driver.save_screenshot("dropdown_opened.png")
                        print("📸 Dropdown opened screenshot: dropdown_opened.png")

                        # Look for options
                        options = driver.find_elements(By.CSS_SELECTOR, "[role='option'], li[role='option'], .MuiAutocomplete-option")
                        print(f"  Found {len(options)} options:")
                        for opt in options[:10]:
                            print(f"    - {opt.text}")

                        break
                    except Exception as e:
                        print(f"  Error: {e}")
        except Exception as e:
            print(f"  MUI Error: {e}")

        print("\n\n⏸️  Browser will stay open for 60 seconds so you can inspect manually...")
        print("Look at the dropdown and note:")
        print("  1. What type of element is it? (select, button, input, etc.)")
        print("  2. What classes does it have?")
        print("  3. How do you open it?")
        print("  4. How are the options displayed?")

        time.sleep(60)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        driver.save_screenshot("error_screenshot.png")

    finally:
        driver.quit()
        print("\n✅ Inspection complete. Check the screenshots and HTML files.")

if __name__ == "__main__":
    inspect_dropdown()
