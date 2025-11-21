# ACME Website Data Capture and Comparison Framework

## Overview
This framework provides automated tools to capture API responses and UI data from the ACME website before and after migration, enabling easy comparison to identify any discrepancies.

## Files Included

1. **[basic_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/basic_capture.py)** - Captures API data using direct HTTP requests
2. **[complete_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/complete_capture.py)** - Captures comprehensive data using Selenium (API responses, screenshots, page sources)
3. **[compare_direct.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/compare_direct.py)** - Compares data captures before and after migration
4. **[requirements.txt](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/requirements.txt)** - Python package dependencies

## Setup Instructions

1. Ensure Python 3.7+ is installed on your system
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage Instructions

### Before Migration (Initial Capture)

Run either the basic or complete capture script:

**Option 1: Basic Capture (faster, API data only)**
```
python basic_capture.py
```

**Option 2: Complete Capture (comprehensive, includes screenshots)**
```
python complete_capture.py
```

Both scripts will:
- Automatically attempt to log in to the ACME website
- Capture API responses from various endpoints
- Save data in a timestamped directory (e.g., `api_captures_20251121_195757`)

### After Migration (Verification Capture)

Run the same capture script you used before migration to capture the post-migration data.

### Comparing Results

Use the comparison script to identify differences between before and after migration:

```
python compare_direct.py <before_migration_directory> <after_migration_directory>
```

Example:
```
python compare_direct.py api_captures_20251121_195757 complete_captures_20251121_195939
```

The comparison will generate two reports in the after migration directory:
1. `migration_comparison_report.json` - Detailed JSON report
2. `migration_differences.txt` - Human-readable summary

## What Gets Captured

### Basic Capture ([basic_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/basic_capture.py))
- API responses from common endpoints
- HTTP status codes and headers
- Response data in JSON format

### Complete Capture ([complete_capture.py](file:///c%3A/Users/Abhiyant/Downloads/sculptsoft/Get%20all_json_response/complete_capture.py))
- All data from basic capture
- Browser screenshots of key pages
- Full page HTML sources
- Visible text content
- Browser network logs (API responses)

## Credentials

The scripts are configured with the following credentials:
- Website: https://acme.qa.egalvanic.ai
- Email: rahul@egalvanic.com
- Password: RP@egalvanic123

## Success Criteria

The automation is successful when it:
1. Captures API responses from the website
2. Saves data in structured, comparable format
3. Enables easy identification of any data changes post-migration
4. Produces consistent, reliable results across multiple runs

## Troubleshooting

### Common Issues

1. **Login failures**: Check credentials in the script files
2. **Timeout errors**: The website may be slow; try running the script again
3. **Missing data**: Some API endpoints may require specific permissions or conditions

### Browser Compatibility

The scripts use Chrome via Selenium. Ensure you have Chrome installed on your system.

## Example Workflow

1. **Before migration**:
   ```
   python basic_capture.py
   # Creates: api_captures_20251121_195757/
   ```

2. **After migration**:
   ```
   python basic_capture.py
   # Creates: api_captures_20251121_201532/
   ```

3. **Compare results**:
   ```
   python compare_direct.py api_captures_20251121_195757 api_captures_20251121_201532
   ```

This will show any differences in API responses between the two captures.