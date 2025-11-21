# Automation Prompt for ACME Website Data Capture

## Objective
Create a fully automated solution to capture all API responses and key UI data from the ACME website (https://acme.qa.egalvanic.ai) before migration, enabling easy comparison with post-migration data to identify any discrepancies.

## Credentials
- Website: https://acme.qa.egalvanic.ai
- Email: rahul@egalvanic.com
- Password: RP@egalvanic123

## Requirements

### Primary Goals
1. **Automated Login**: Script should automatically log into the ACME website using provided credentials
2. **Complete Data Capture**: Capture all accessible API responses and key UI data
3. **Organized Storage**: Save each response as separate local JSON files, organized by endpoint/section
4. **Future Comparison Ready**: Structure data to enable easy automated comparison after migration
5. **Minimal Manual Work**: Fully automated solution with no copy-pasting required

### Technical Specifications
- Use any preferred technology (Python with Selenium recommended)
- Capture both API responses and relevant UI data
- Handle authentication/session management properly
- Store data in structured, comparable format
- Include timestamps and metadata for tracking

## Implementation Framework

### Provided Solution Components

1. **[simple_api_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/simple_api_capture.py)** - Main automation script that:
   - Automatically downloads and manages ChromeDriver
   - Logs into the ACME website
   - Navigates through key pages to trigger API calls
   - Captures all API responses via browser network interception
   - Saves each response as individual JSON files
   - Creates organized directory structure with timestamps

2. **[compare_captures.py](file:///c%2FUsers%2FAbhiyant%2FDownloads%2Fsculptsoft%2FGet%20all_json_response%2Fcompare_captures.py)** - Comparison tool that:
   - Compares pre-migration and post-migration data
   - Identifies added, removed, or changed API responses
   - Generates detailed diff reports
   - Provides human-readable comparison summaries

3. **[requirements.txt](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/requirements.txt)** - Python package dependencies

4. **[run_capture.bat](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/run_capture.bat)** - Windows batch script for easy execution

### Directory Structure
```
acme_data_capture/
├── simple_api_capture.py       # Main capture script
├── compare_captures.py         # Comparison tool
├── requirements.txt            # Dependencies
├── run_capture.bat             # Windows execution script
└── api_captures_TIMESTAMP/     # Output data (created on each run)
    ├── response_1.json         # Individual API responses
    ├── response_2.json
    ├── all_responses.json      # Consolidated responses
    └── capture_summary.json    # Capture metadata
```

## Usage Instructions

### Before Migration (Initial Capture)
1. Ensure Python 3.7+ is installed on the system
2. Execute [run_capture.bat](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/run_capture.bat) (Windows) or run:
   ```
   pip install -r requirements.txt
   python simple_api_capture.py
   ```
3. Script will automatically:
   - Launch Chrome browser
   - Log in with provided credentials
   - Navigate through key pages
   - Capture all API responses
   - Save data in timestamped directory

### After Migration (Verification Capture)
1. Run the same capture process as before migration
2. This creates a second timestamped directory with new data

### Comparing Results
1. Run the comparison tool:
   ```
   python compare_captures.py
   ```
2. Select the pre-migration and post-migration directories when prompted
3. Tool generates:
   - JSON report with detailed differences
   - Human-readable text report with diffs
   - Summary of added/removed/changed endpoints

## Expected Output Format

Each API response is saved as a separate JSON file with this structure:
```json
{
  "url": "https://acme.qa.egalvanic.ai/api/sites",
  "status": 200,
  "mimeType": "application/json",
  "timestamp": 1234567890123.456,
  "response": {
    // Actual API response data
  }
}
```

## Key Benefits

1. **Fully Automated**: No manual intervention required after initial setup
2. **Comprehensive Coverage**: Captures all API responses automatically
3. **Easy Comparison**: Structured output enables automated diff checking
4. **Self-Contained**: Automatic dependency management
5. **Cross-Platform**: Works on Windows, macOS, and Linux
6. **Extensible**: Easy to add new endpoints or modify capture logic

## Adaptation for Other Tools

This framework can be adapted for use with other automation tools:

### For Cursor or Similar AI Coding Assistants
- Provide the entire codebase and directory structure
- Specify the exact requirements as outlined in this prompt
- Request generation of any missing components or modifications

### For CI/CD Integration
- Script can be integrated into automated testing pipelines
- Results can be published as artifacts for comparison
- Failures can be flagged if critical API changes are detected

## Success Criteria

The automation is successful when it:
1. Logs into the website without manual intervention
2. Captures all API responses from key application pages
3. Saves data in structured, comparable format
4. Enables easy identification of any data changes post-migration
5. Produces consistent, reliable results across multiple runs

This solution eliminates the need for manual copying/pasting of responses and provides a robust framework for migration verification.