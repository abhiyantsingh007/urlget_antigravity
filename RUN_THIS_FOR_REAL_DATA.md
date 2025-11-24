# 🎯 READY TO RUN - Get Your Complete Comparison Report

## What You See Now (Demo Report)

The report that just opened in your browser is a **DEMO** showing the format. It includes sample data for:
- Site657: 1 → 0 assets (CRITICAL)
- All Facilities: 2,535 → 1,048 assets (MAJOR)
- London UK: 450 → 445 assets (MINOR)
- And all metrics across all tabs

## To Get YOUR REAL DATA (Including Super Caremark)

### ⚡ Quick Method (Automated - Recommended)

Just run this one command:

```bash
./run_full_comparison.sh
```

It will:
1. Ask for your email/password
2. Capture RND website (all sites)
3. Capture AI website (all sites)
4. Generate the comparison report
5. Open it automatically

**That's it!** You'll get a report showing ALL sites including Super Caremark: 179 → 180.

### 🛠️ Manual Method (Step by Step)

If you prefer to run it manually:

#### Step 1: Capture RND Website
```bash
python3 capture_all_sites.py https://acme.egalvanic-rnd.com your@email.com your_password
```

When asked "Capture NEW website?", answer **n** (we'll do it separately)

#### Step 2: Capture AI Website  
```bash
python3 capture_all_sites.py https://acme.qa.egalvanic.ai your@email.com your_password
```

When asked "Capture NEW website?", answer **n**

#### Step 3: Compare
```bash
# Find the capture directories created above
ls -la | grep capture

# Then compare them
python3 site_data_comparator.py old_all_sites_capture new_all_sites_capture

# Open the report
open site_comparison_report.html
```

## What You'll Get

A complete HTML report with a table like this:

| Site Name | Field | Old (RND) | New (AI) | Change | Severity |
|-----------|-------|-----------|----------|--------|----------|
| **Super Caremark** | total_assets | 179 | 180 | +1 | 🟡 MINOR |
| **Super Caremark** | open_issues | 12 | 10 | -2 | 🟡 MINOR |
| **Site657** | total_assets | 1 | 0 | -1 | 🔴 CRITICAL |
| **All Facilities** | total_assets | 2,535 | 1,048 | -1,487 | 🟠 MAJOR |
| **All Facilities** | open_issues | 71 | 57 | -14 | 🟡 MINOR |
| **London UK** | total_assets | 450 | 445 | -5 | 🟡 MINOR |
| ... | ... | ... | ... | ... | ... |

**Every single site from the dropdown** with **all their metrics** compared!

## Troubleshooting

### If `./run_full_comparison.sh` doesn't work:

```bash
# Make it executable first
chmod +x run_full_comparison.sh

# Then run it
./run_full_comparison.sh
```

### If the script can't find the site dropdown:

The tool looks for common dropdown patterns. If it can't find yours:

1. Run with visible browser (edit capture_all_sites.py, comment out `--headless`)
2. Watch what happens
3. Tell me the CSS selector of your site dropdown
4. I'll update the script

### If Super Caremark still doesn't show:

Make sure:
1. Super Caremark is in the site dropdown on both websites
2. You can manually select it and see the data
3. The data loads when you select it

If yes to all above, the tool will capture it!

## Expected Runtime

- **Per website:** ~2-5 minutes (depending on number of sites)
- **Total:** ~10 minutes for both sites + comparison

The script shows progress like:
```
[1/45] Capturing: Super Caremark
   ✅ Captured 5 metrics: ['total_assets', 'open_issues', ...]
[2/45] Capturing: Site657
   ✅ Captured 5 metrics: ['total_assets', 'open_issues', ...]
...
```

## Files You'll Get

- 📊 **site_comparison_report.html** - The main report (share this!)
- 📁 **old_all_sites_capture/** - RND website data
- 📁 **new_all_sites_capture/** - AI website data  
- 📸 **Screenshots** for each site

## Ready?

Run this now:
```bash
./run_full_comparison.sh
```

Or manually:
```bash
python3 capture_all_sites.py https://acme.egalvanic-rnd.com your@email.com password
```

You'll see Super Caremark (179 → 180) in your report! 🎯
