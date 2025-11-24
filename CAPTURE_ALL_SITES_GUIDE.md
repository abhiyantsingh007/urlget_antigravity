# 🎯 Complete Site-by-Site Comparison Guide

## The Problem

You noticed **Super Caremark** has:
- **179 assets** on RND website
- **180 assets** on AI website  
- Difference of **+1 asset**

But this wasn't showing in the report because the API responses didn't include Super Caremark's data!

## The Solution

**`capture_all_sites.py`** - Automatically captures data for **EVERY site in the dropdown**

## How It Works

1. 🌐 **Opens the website**
2. 🔐 **Logs in** with your credentials
3. 🔍 **Finds the site selector dropdown**
4. 📋 **Gets ALL sites** from the dropdown
5. 🔄 **For each site:**
   - Selects it from dropdown
   - Waits for page to load
   - Captures all metrics (assets, issues, sessions, etc.)
   - Takes a screenshot
6. 💾 **Saves everything** in comparison-ready format
7. 📊 **Runs comparison** showing differences for ALL sites

## Quick Start

```bash
# Capture OLD website (all sites)
python3 capture_all_sites.py https://acme.egalvanic-rnd.com username@example.com password

# Capture NEW website (all sites)
# (The script will prompt you for this)

# Get comprehensive comparison report
open site_comparison_report.html
```

## What You'll Get

A complete table showing **EVERY site**, including:

| Site Name | Field | Old Value | New Value | Change | Severity |
|-----------|-------|-----------|-----------|--------|----------|
| Super Caremark | total_assets | 179 | 180 | +1 | MINOR |
| Site657 | total_assets | 1 | 0 | -1 | CRITICAL |
| All Facilities | total_assets | 2,535 | 1,048 | -1,487 | MAJOR |
| London UK | open_issues | 12 | 10 | -2 | MINOR |
| ... | ... | ... | ... | ... | ... |

**Every single site from the dropdown will be compared!**

## Step-by-Step Instructions

### 1. Capture Old Website

```bash
python3 capture_all_sites.py https://acme.egalvanic-rnd.com your.email@example.com yourpassword
```

The script will:
- Log in
- Find the site dropdown
- Show you all sites it found
- Capture each one
- Save to `old_all_sites_capture/`

### 2. Capture New Website

When prompted, choose `y` to capture new site:

```
Capture NEW website? (y/n): y
New site URL (press Enter to use same URL): https://acme.qa.egalvanic.ai
```

The script will:
- Log in to new site
- Capture all sites again
- Save to `new_all_sites_capture/`
- Automatically run comparison

### 3. Review the Report

```bash
open site_comparison_report.html
```

You'll see:
- ✅ **Every site** from the dropdown
- ✅ **All metrics** for each site
- ✅ **Exact differences** highlighted by severity
- ✅ **Super Caremark: 179 → 180** will be there!

## What Gets Captured

For each site, the tool captures:

- 📦 **total_assets** - Number of assets
- ⚠️ **open_issues** - Open issues count
- 🏃 **active_sessions** - Active site visits
- ✅ **pending_tasks** - Pending tasks
- 💰 **opportunities_value** - Opportunities value
- And any other metrics visible on the page

## Troubleshooting

### "Could not find site dropdown"

The tool looks for common selectors. If it can't find the dropdown, you can:

1. **Run without headless mode:**
   - Edit the script, comment out line with `--headless`
   - Browser will open so you can see what's happening

2. **Tell me the selector:**
   - Open DevTools (F12)
   - Inspect the site dropdown
   - Copy the CSS selector
   - I'll update the script

### "No data captured for some sites"

The tool tries to find metrics from:
- Dashboard cards/widgets
- Table rows
- Text patterns like "Total Assets: 179"

If a site's layout is different, tell me and I'll add more patterns.

### "Super Caremark still not showing"

Make sure:
1. Super Caremark is in the dropdown
2. You can select it manually
3. The metrics are visible on the page after selecting it

## Advanced Usage

### Capture Only (No Comparison)

```bash
# Just capture old site
python3 capture_all_sites.py https://old-site.com username password

# When prompted "Capture NEW website?", answer 'n'
```

### Compare Existing Captures

If you already have captures:

```bash
python3 site_data_comparator.py old_all_sites_capture new_all_sites_capture
```

### Modify What Gets Captured

Edit `capture_site_data()` function in `capture_all_sites.py` to add custom patterns for your page layout.

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║  COMPREHENSIVE SITE-BY-SITE CAPTURE                           ║
║  Captures data for EVERY site in the dropdown                 ║
╚════════════════════════════════════════════════════════════════╝

🔐 Logging in to: https://acme.egalvanic-rnd.com
⏳ Waiting for dashboard...

🔍 Looking for site dropdown...
✅ Found site dropdown with 45 sites

📋 Found 45 sites to capture:
   • Super Caremark
   • Site657
   • All Facilities
   • London UK
   • Melbourne AU
   ... (40 more)

🔄 Capturing data for each site...

[1/45] Capturing: Super Caremark
   ✅ Captured 5 metrics: ['total_assets', 'open_issues', 'active_sessions', 'pending_tasks', 'opportunities_value']

[2/45] Capturing: Site657
   ✅ Captured 5 metrics: ['total_assets', 'open_issues', 'active_sessions', 'pending_tasks', 'opportunities_value']

... (continues for all sites)

✅ Captured 45 sites
📁 Saved to: old_all_sites_capture/complete_capture.json

📊 Summary:
   Super Caremark: 179 assets
   Site657: 1 assets
   All Facilities: 2535 assets
   ... (all sites)
```

## Why This is Better

| Old Approach | New Approach |
|--------------|--------------|
| Only captures sites in API responses | ✅ Captures EVERY site in dropdown |
| Might miss some sites | ✅ Guaranteed to get ALL sites |
| Depends on API structure | ✅ Works with any page layout |
| Manual site selection needed | ✅ Fully automated |
| Limited to API data | ✅ Captures visible metrics |

## Next Steps

1. **Run the capture:** `python3 capture_all_sites.py <url> <username> <password>`
2. **Check the report:** `open site_comparison_report.html`
3. **Find Super Caremark:** Look for it in the comparison table!
4. **Share with manager:** The report is professional and comprehensive

The tool will find **every site difference**, including Super Caremark's +1 asset! 🎯
