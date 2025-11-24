# Enhanced Site Data Capture Framework

This enhanced framework automatically captures API responses and page data for ALL sites in the site dropdown, not just ShowSite3. It ensures comprehensive data collection before and after migration.

## Features

- **Complete Site Coverage**: Captures data for all sites in the dropdown menu
- **Automatic Site Navigation**: Iterates through each site automatically
- **Comprehensive Data Collection**: Captures API responses, screenshots, page sources, and visible text for each site
- **Organized Storage**: Saves all data in a structured directory format
- **Pre/Post Migration Comparison**: Ready for comparison after migration

## How It Works

1. **Login**: Automatically logs into the ACME website
2. **Site Discovery**: Identifies all sites in the site dropdown
3. **Site Iteration**: For each site:
   - Selects the site from the dropdown
   - Captures screenshots of the site overview
   - Saves page source and visible text
   - Navigates to related pages (assets, arc flash, resolved issues, reports)
   - Captures data for each page
   - Records all API responses automatically
4. **Data Organization**: Saves all data in timestamped directories

## Directory Structure

```
enhanced_site_capture_20231121_100000/
├── capture_summary.json
└── sites/
    ├── London UK/
    │   ├── api_responses/
    │   │   ├── response_1.json
    │   │   ├── response_2.json
    │   │   └── ...
    │   ├── screenshots/
    │   │   ├── London_UK_overview.png
    │   │   ├── assets.png
    │   │   └── ...
    │   ├── page_source.html
    │   └── visible_text.txt
    ├── All Facilities/
    │   ├── api_responses/
    │   ├── screenshots/
    │   ├── page_source.html
    │   └── visible_text.txt
    └── ... (other sites)
```

## Usage

1. Update credentials in [run_enhanced_capture.py](file:///Users/vishwa/Downloads/urlget/run_enhanced_capture.py) if needed
2. Run the enhanced capture script:
   ```bash
   python run_enhanced_capture.py
   ```

3. The script will:
   - Create a timestamped output directory
   - Log in to the website (https://acme.egalvanic.ai)
   - Discover all sites in the dropdown
   - Capture comprehensive data for each site
   - Save all data in organized directories

## API Response Format

Each API response is saved as a JSON file with full metadata:
```json
{
  "url": "https://acme.egalvanic.ai/api/assets",
  "status": 200,
  "mimeType": "application/json",
  "timestamp": 1234567890123,
  "response": {
    "assets": [
      {
        "id": 1,
        "name": "Transformer T1",
        "type": "Electrical",
        "status": "Operational"
      }
    ]
  },
  "site": "London UK"
}
```

## Benefits

1. **Complete Coverage**: No longer limited to ShowSite3 - captures data for all sites
2. **No Manual Work**: Fully automated site iteration and data capture
3. **Easy Comparison**: Structured data organization makes post-migration comparison simple
4. **Comprehensive**: Captures all relevant data for each site
5. **Reliable**: Handles site dropdown interaction automatically