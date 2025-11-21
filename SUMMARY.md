# ACME Website Data Capture Automation

## Overview
This automation framework captures all API responses from the ACME website (https://acme.qa.egalvanic.ai) to enable easy comparison before and after migration. The solution eliminates manual copying/pasting of responses and provides automated verification capabilities.

## Files Provided

1. **[simple_api_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/simple_api_capture.py)** - Main automation script
2. **[compare_captures.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/compare_captures.py)** - Comparison tool for pre/post migration data
3. **[requirements.txt](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/requirements.txt)** - Python dependencies
4. **[run_capture.bat](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/run_capture.bat)** - Windows execution script
5. **[AUTOMATION_PROMPT.md](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/AUTOMATION_PROMPT.md)** - Detailed automation prompt for AI tools

## Quick Start (Windows)

1. Ensure Python 3.7+ is installed
2. Double-click [run_capture.bat](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/run_capture.bat) to run the capture
3. Data will be saved in a timestamped folder (e.g., `api_captures_20231121_120000`)

## Manual Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run data capture
python simple_api_capture.py

# Compare captures (after running twice)
python compare_captures.py
```

## How It Works

1. **Automated Login**: Script logs into ACME website with provided credentials
2. **Page Navigation**: Automatically visits key pages to trigger API calls
3. **Response Capture**: Intercepts all API responses via browser network logs
4. **Data Storage**: Saves each response as individual JSON files
5. **Comparison Ready**: Organizes data for easy pre/post migration comparison

## Output Structure

```
api_captures_20231121_120000/
├── response_1.json          # Individual API response
├── response_2.json
├── all_responses.json       # Consolidated responses
└── capture_summary.json     # Capture metadata
```

## Credentials

- Website: https://acme.qa.egalvanic.ai
- Email: rahul@egalvanic.com
- Password: RP@egalvanic123

## Benefits

- ✅ **Fully Automated** - No manual intervention required
- ✅ **Complete Coverage** - Captures all API responses automatically
- ✅ **Easy Comparison** - Structured output for automated diff checking
- ✅ **Self-Contained** - Automatic dependency management
- ✅ **Cross-Platform** - Works on Windows, macOS, and Linux

## For AI Tools (Cursor, etc.)

To recreate this solution using AI coding assistants:

1. Provide the [AUTOMATION_PROMPT.md](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/AUTOMATION_PROMPT.md) file
2. Specify the technology stack (Python + Selenium recommended)
3. Request implementation of each component as needed

This framework provides a robust solution for migration verification with minimal manual effort.