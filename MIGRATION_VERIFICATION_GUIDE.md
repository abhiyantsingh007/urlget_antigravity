# 🚀 Automated Migration Verification System

## Quick Start Guide

This system automatically captures ALL API responses from your websites and compares them to detect data loss issues like Site657's asset count problem.

## 📋 Prerequisites

```bash
pip install selenium webdriver-manager
```

## 🔧 Usage

### Step 1: Capture Old Website Data (Do this BEFORE migration)

```bash
python3 automated_migration_capture.py \
  --url https://acme.rnd.egalvanic.com \
  --output old
```

This creates `old_capture.json` with ALL API responses from the old website.

### Step 2: Capture New Website Data (Do this AFTER migration)

```bash
python3 automated_migration_capture.py \
  --url https://acme.egalvanic.ai \
  --output new
```

This creates `new_capture.json` with ALL API responses from the new website.

### Step 3: Compare and Generate Report

```bash
python3 automated_migration_comparison.py old_capture.json new_capture.json
```

This generates `migration_verification_report.html` showing:
- ✅ All Site657 and other site comparisons
- 🔴 CRITICAL issues (like 1 → 0 assets)
- 🟡 MAJOR differences
- ⚪ MINOR changes

## 📊 What Gets Captured

The system automatically captures API responses from:
- `/dashboard` - Overall dashboard data
- `/sites` - Site listings and details
- `/assets` - Asset information
- `/issues` - Issue counts
- `/reports` - Report data

**Everything is automatic - NO manual copy-paste needed!**

## 🎯 What Gets Detected

The comparison script automatically detects and flags:

### CRITICAL Issues
- Assets changing from positive number to ZERO (like Site657: 1 → 0)
- Sites completely missing from new website

### MAJOR Issues
- Large changes in asset counts (>100 difference)
- Significant data variations

### MINOR Issues
- Small numerical changes
- Expected variations

## 📁 Output Files

- `old_capture.json` - All API responses from old website
- `new_capture.json` - All API responses from new website
- `migration_verification_report.html` - Beautiful HTML report with all comparisons

## 🔍 Example: Site657 Detection

**Old Website:** Site657 has 1 asset
**New Website:** Site657 has 0 assets
**Result:** Report shows this as **CRITICAL** with red badge

## ⚡ Pro Tips

1. **Run Step 1 NOW** (before migration) to save current state
2. **Run Steps 2-3** after migration to compare
3. **Re-run comparison** after fixing issues to verify
4. **Keep all JSON files** for historical records

## 🆘 Troubleshooting

If capture fails:
1. Check login credentials in the script (default: rahul+acme@egalvanic.com)
2. Ensure you have internet access
3. Check that the website is accessible

## 📞 Quick Reference

```bash
# Full workflow (save this!)
# BEFORE migration:
python3 automated_migration_capture.py --url https://acme.rnd.egalvanic.com --output old

# AFTER migration:
python3 automated_migration_capture.py --url https://acme.egalvanic.ai --output new
python3 automated_migration_comparison.py old_capture.json new_capture.json

# Then open: migration_verification_report.html
```

---

**No more manual work! Everything is automated. Just run the commands and get your report!** ✨
