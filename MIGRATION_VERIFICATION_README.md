# Migration Verification Framework

This framework verifies that all data has been correctly migrated from the old website (https://acme.egalvanic-rnd.com) to the new migration website (https://acme.egalvanic.ai).

## Purpose

The migration verification framework ensures data integrity during the website migration process by:
1. Capturing data from the old website
2. Capturing data from the new migration website
3. Comparing the data between both websites
4. Generating detailed reports on any discrepancies

## How It Works

1. **Login**: Automatically logs into both the old and new websites
2. **Data Capture**: For each site in the dropdown:
   - Captures page source HTML
   - Extracts visible text content
3. **Data Comparison**: Compares captured data between old and new websites
4. **Reporting**: Generates detailed comparison reports

## Directory Structure

```
migration_verification_20231121_100000/
├── verification_summary.json
├── old_website_data/
│   ├── London UK/
│   │   ├── page_source.html
│   │   └── visible_text.txt
│   └── ... (other sites)
├── new_website_data/
│   ├── London UK/
│   │   ├── page_source.html
│   │   └── visible_text.txt
│   └── ... (other sites)
└── comparison_results/
    ├── London_UK_comparison.json
    └── ... (other sites)
```

## Usage

1. Update credentials in [run_migration_verification.py](file:///Users/vishwa/Downloads/urlget/run_migration_verification.py) if needed
2. Run the migration verification script:
   ```bash
   python run_migration_verification.py
   ```

3. The script will:
   - Create a timestamped output directory
   - Log in to the old website (https://acme.egalvanic-rnd.com)
   - Capture data for all sites
   - Log in to the new website (https://acme.egalvanic.ai)
   - Capture data for all sites
   - Compare data between websites
   - Generate detailed reports

## Verification Process

The framework verifies data integrity by comparing:
- **Page Source**: Complete HTML content of each page
- **Visible Text**: Text content visible to users

## Comparison Result Format

Each comparison result is saved as a JSON file:
```json
{
  "site": "London UK",
  "comparison_timestamp": "2023-11-21T10:00:00.123456",
  "differences": [
    {
      "type": "page_source",
      "status": "different",
      "details": "Page source content differs between old and new websites"
    }
  ]
}
```

## Benefits

1. **Complete Verification**: Checks all sites in the dropdown
2. **Automated Process**: No manual intervention required
3. **Detailed Reporting**: Clear identification of discrepancies
4. **Data Integrity**: Ensures no data loss during migration
5. **Easy Analysis**: Structured output for quick review