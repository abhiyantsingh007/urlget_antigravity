# ACME Website Migration Data Capture and Comparison Framework

This framework automatically captures all API responses and page data from the ACME website before and after migration to ensure no data loss during the migration process.

## Features

- **Automatic API Response Capture**: Captures all JSON API responses automatically without manual intervention
- **Complete Page Data Collection**: Captures screenshots, page sources, and visible text from all pages
- **Pre/Post Migration Comparison**: Automatically compares data to detect any discrepancies
- **Organized Data Storage**: Saves all data in timestamped directories for easy tracking

## Setup

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Update the credentials in the scripts:
   - Edit `run_pre_migration_capture.py` and `run_post_migration_capture.py`
   - Update `EMAIL` and `PASSWORD` variables with valid login credentials

## Usage

### Before Migration (Pre-Migration Capture)

1. Run the pre-migration capture script:
   ```bash
   python run_pre_migration_capture.py
   ```

2. The script will:
   - Automatically log in to the website
   - Navigate to all pages (dashboard, sites, assets, issues, reports, settings, profile)
   - Capture screenshots, page sources, and visible text for each page
   - Automatically capture all API responses in JSON format
   - Save all data in a timestamped directory (e.g., `pre_migration_capture_20231121_100000`)

### After Migration (Post-Migration Capture and Comparison)

1. Run the post-migration capture script:
   ```bash
   python run_post_migration_capture.py
   ```

2. The script will:
   - Automatically detect the most recent pre-migration capture
   - Run the post-migration capture (same process as pre-migration)
   - Automatically compare pre and post migration data
   - Generate detailed comparison reports

## Data Structure

Each capture creates a directory with the following structure:
```
pre_migration_capture_20231121_100000/
├── api_responses/
│   ├── response_1.json
│   ├── response_2.json
│   └── all_responses.json
├── screenshots/
│   ├── dashboard.png
│   ├── sites.png
│   └── ...
├── page_sources/
│   ├── dashboard.html
│   ├── sites.html
│   └── ...
├── visible_texts/
│   ├── dashboard.txt
│   ├── sites.txt
│   └── ...
├── capture_summary.json
└── content_comparison_report.json (created during comparison)
```

## Manual Comparison

If you need to manually compare captures:
```python
from pre_migration_capture import compare_pre_post_migration
compare_pre_post_migration('pre_migration_capture_20231121_100000', 'post_migration_capture_20231122_150000')
```

## Important Notes

- The framework automatically handles ChromeDriver installation
- All API responses are captured automatically without manual copying
- The comparison tool will detect missing, added, or changed API responses
- Screenshots and page content help identify UI changes
- Run the pre-migration capture before the website migration next week