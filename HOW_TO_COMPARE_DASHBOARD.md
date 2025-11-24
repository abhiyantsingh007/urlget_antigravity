# 🏢 Comprehensive Dashboard Comparison - How To Use

## What You Get

The **site_data_comparator.py** tool compares **ALL metrics from ALL dashboard tabs** across all your sites, including:

### 📊 Assets Tab
- total_assets
- asset_count

### ⚠️ Issues Tab
- open_issues
- unresolved_issues
- resolved_issues
- total_issues

### 🏃 Site Visits Tab
- active_sessions
- completed_sessions
- total_sessions

### ✅ Tasks Tab
- pending_tasks
- completed_tasks
- total_tasks

### 💰 Opportunities Tab
- opportunities_value
- opportunities_count

### 🔧 Equipment Tab
- equipment_at_risk

### 📈 Reports/Analytics
- compliance_score
- safety_score

## Example Output

The report generates a table like this:

| Site Name | Field | Old Value | New Value | Change | Severity |
|-----------|-------|-----------|-----------|--------|----------|
| **Site657** | total_assets | 1 | 0 | -1 | CRITICAL |
| **All Facilities** | total_assets | 2,535 | 1,048 | -1,487 | MAJOR |
| **All Facilities** | open_issues | 71 | 57 | -14 | MINOR |
| **All Facilities** | opportunities_value | 485,000 | 334,000 | -151,000 | MAJOR |
| **All Facilities** | equipment_at_risk | 1,200,000 | 950,000 | -250,000 | MAJOR |
| **London UK** | total_assets | 450 | 445 | -5 | MINOR |
| **London UK** | resolved_issues | 45 | 47 | +2 | MINOR |

...and so on for ALL sites and ALL fields!

## How to Use With Your Real Data

### Option 1: Manual Capture (Recommended for Testing)

1. **Find the dashboard API endpoint** that returns all sites data. Common endpoints:
   - `/api/dashboard/sites`
   - `/api/sites/overview`
   - `/api/company/dashboard`

2. **Capture the data manually:**
   ```bash
   # In your browser, open DevTools (F12)
   # Go to Network tab
   # Navigate to the dashboard page
   # Find the API call that returns all sites data
   # Copy the response
   # Save as old_dashboard/complete_capture.json and new_dashboard/complete_capture.json
   ```

3. **Run comparison:**
   ```bash
   python3 site_data_comparator.py old_dashboard new_dashboard
   ```

### Option 2: Automated Capture (For Production Use)

1. **Capture old site:**
   ```bash
   python3 capture_dashboard.py https://old-site.example.com username password
   ```

2. **Capture new site:**
   ```bash
   python3 capture_dashboard.py https://new-site.example.com username password
   ```

3. **Compare:**
   ```bash
   python3 site_data_comparator.py old_dashboard_capture_TIMESTAMP new_dashboard_capture_TIMESTAMP
   ```

### Option 3: Use Existing Capture Data

If you already have API response captures:

```bash
python3 site_data_comparator.py /path/to/old/capture /path/to/new/capture
```

## Data Format Required

Your capture data should be JSON in this format:

```json
{
  "api_responses": [{
    "url": "https://example.com/api/dashboard/sites",
    "response": {
      "sites": {
        "Site657": {
          "name": "Site657",
          "total_assets": 1,
          "open_issues": 5,
          "active_sessions": 2,
          "pending_tasks": 3,
          "opportunities_value": 50000,
          ...  (all other fields)
        },
        "All Facilities": {
          "name": "All Facilities",
          "total_assets": 2535,
          ...
        }
      }
    }
  }]
}
```

## Understanding the Report

### Severity Levels

| Severity | When | Example |
|----------|------|---------|
| **CRITICAL** | Data loss (positive → 0) | Assets: 1 → 0 |
| **MAJOR** | Large change (>100 units or >30%) | Assets: 2535 → 1048 (-1487) |
| **MINOR** | Small change | Assets: 450 → 445 (-5) |

### Color Coding in Report

- 🔴 **Red** = Critical Issues
- 🟠 **Orange** = Major Differences  
- 🟡 **Yellow** = Minor Changes
- 🟢 **Green** = Positive changes (increases)

## What the Tool Does

1. ✅ **Loads old and new capture data**
2. ✅ **Extracts ALL metrics for each site**
3. ✅ **Compares every field** between old and new
4. ✅ **Classifies severity** (Critical/Major/Minor)
5. ✅ **Generates comprehensive HTML report**
6. ✅ **Shows exact values** and changes
7. ✅ **Highlights issues** with color coding

## Files Generated

After running the comparison:

- **site_comparison_report.html** - Beautiful visual report (share this with your manager!)
- **site_comparison_report.json** - Raw data for programmatic access

## Demo

To see how it works with sample data:

```bash
python3 demo_site_comparison.py
open site_comparison_report.html
```

This creates demo data showing:
- Critical data loss (Site657)
- Major asset changes (All Facilities)
- Changes across all tabs (open_issues, active_sessions, pending_tasks, etc.)

## Quick Start

```bash
# See the demo
python3 demo_site_comparison.py

# For your real data, tell the tool where to find your captures
python3 site_data_comparator.py <old_capture_directory> <new_capture_directory>
```

## Troubleshooting

### "No sites found"
- Your API response structure might be different
- Check that the response has a "sites" object
- Or modify `_extract_sites_data()` in the code to match your API structure

### "Failed to load capture data"
- Make sure you have `complete_capture.json` in the directory
- Or one of: `complete_tab_capture.json`, `api_capture.json`

### "Not all fields showing"
- Add your custom field names to `metric_mappings` in `_extract_metrics()`
- The tool will then extract and compare those fields too

## Next Steps

1. **Try the demo** to see what the report looks like
2. **Find your dashboard API endpoint** (check DevTools Network tab)
3. **Capture both old and new data** (manually or with the tool)
4. **Run the comparison** and get your comprehensive report!

The tool is ready to compare **everything** - you just need to point it at the right data! 🚀
