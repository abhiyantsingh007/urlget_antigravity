import json
import os
import time
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

def capture_api_data():
    """Capture API data using direct HTTP requests"""
    
    # Configuration with correct credentials
    BASE_URL = "https://acme.qa.egalvanic.ai"
    EMAIL = "rahul+acme@egalvanic.com"  # Corrected email
    PASSWORD = "RP@egalvanic123"
    
    # Create output directory
    output_dir = "api_captures_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Create a session
    session = requests.Session()
    
    # Try to login
    print("Attempting to login...")
    try:
        # First, get the login page to retrieve any CSRF tokens or session cookies
        login_page = session.get(f"{BASE_URL}/login")
        print(f"Login page status: {login_page.status_code}")
        
        # Try to login with credentials
        login_data = {
            "email": EMAIL,
            "password": PASSWORD
        }
        
        # Try different login endpoints
        login_endpoints = [
            "/login",
            "/auth/login",
            "/api/login"
        ]
        
        login_response = None
        for endpoint in login_endpoints:
            try:
                login_response = session.post(f"{BASE_URL}{endpoint}", data=login_data)
                print(f"Login attempt to {endpoint}: {login_response.status_code}")
                if login_response.status_code == 200:
                    break
            except Exception as e:
                print(f"Login to {endpoint} failed: {str(e)}")
                continue
        
        if login_response and login_response.status_code == 200:
            print("Login successful!")
        else:
            print("Login may have failed, continuing anyway...")
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        print("Continuing without authentication...")
    
    # Common API endpoints to try
    api_endpoints = [
        "/api/sites",
        "/api/users/profile",
        "/api/dashboard/stats",
        "/api/notifications",
        "/api/sites/list",
        "/api/sites/all"
    ]
    
    captured_responses = []
    response_count = 0
    
    # Try to capture data from API endpoints
    for endpoint in api_endpoints:
        try:
            print(f"Fetching {endpoint}...")
            response = session.get(f"{BASE_URL}{endpoint}")
            
            # If we get a successful response, save it
            if response.status_code == 200:
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                # Save response data
                api_entry = {
                    'url': f"{BASE_URL}{endpoint}",
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'response': response_data
                }
                
                captured_responses.append(api_entry)
                response_count += 1
                
                # Save to file
                filename = f"response_{response_count}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(api_entry, f, indent=2, default=str)
                
                print(f"Saved response from {endpoint} to {filename}")
            else:
                print(f"Failed to fetch {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching {endpoint}: {str(e)}")
    
    # Save all responses to a single file
    all_responses_file = os.path.join(output_dir, "all_responses.json")
    with open(all_responses_file, 'w') as f:
        json.dump(captured_responses, f, indent=2, default=str)
    
    # Create summary
    summary = {
        "capture_timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "endpoints_attempted": api_endpoints,
        "responses_captured": response_count,
        "output_directory": output_dir
    }
    
    summary_file = os.path.join(output_dir, "capture_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nCapture completed!")
    print(f"Total API responses captured: {response_count}")
    print(f"Data saved to: {output_dir}")
    
    return output_dir

if __name__ == "__main__":
    capture_api_data()