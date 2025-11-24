# ACME Data Capture Framework

This framework automates the process of capturing API responses and UI data from the ACME website before migration, allowing for easy comparison after migration.

## Features

- Automated login to ACME website
- Capture of API responses from various endpoints
- Collection of UI data from dashboard and key pages
- Screenshots of important pages
- Organized storage of all captured data
- Comparison tool for pre/post migration analysis

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed

## Installation

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Download ChromeDriver (if not using webdriver-manager):
   - Visit https://chromedriver.chromium.org/
   - Download the version compatible with your Chrome browser
   - Add it to your PATH

## Usage

### 1. Running the Data Capture

1. Update the credentials in [data_capture_framework.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/data_capture_framework.py) if needed:
   ```python
   
   ```

2. Run the capture script:
   ```
   python data_capture_framework.py
   ```

3. The script will:
   - Launch Chrome browser
   - Log in automatically
   - Navigate through key pages
   - Capture API responses and UI data
   - Save all data in timestamped folders

### 2. Data Organization

After running, data will be organized in a folder named `captured_data_<timestamp>`:

```
captured_data_20231121_120000/
├── api_responses/
│   ├── sites.json
│   ├── profile.json
│   └── stats.json
├── ui_data/
│   └── dashboard_ui.json
├── screenshots/
│   ├── dashboard.png
│   ├── sites.png
│   └── profile.png
├── api_calls_summary.json
└── capture_summary.json
```

### 3. Post-Migration Comparison

After migration, run the capture again to get new data, then compare:

```python
from data_capture_framework import compare_data

# Compare old and new data
results = compare_data('captured_data_20231121_120000', 'captured_data_20231122_140000')
```

## Customization

### Adding API Endpoints

Modify the `api_endpoints` list in the `capture_api_responses` method:

```python
api_endpoints = [
    "/api/sites",
    "/api/users/profile",
    "/api/dashboard/stats",
    "/api/notifications",
    # Add your additional endpoints here
]
```

### Adding UI Elements

Modify the selectors in the `capture_ui_data` method to capture specific elements from your application.

## Troubleshooting

### Common Issues

1. **Login fails**: Check credentials in the script
2. **Elements not found**: Update CSS selectors based on the actual website structure
3. **ChromeDriver issues**: Ensure ChromeDriver version matches your Chrome browser

### Browser Compatibility

This script is designed for Chrome. For other browsers, modify the driver initialization in `setup_driver()`.

## License

This project is licensed under the MIT License.# urlget_antigravity
