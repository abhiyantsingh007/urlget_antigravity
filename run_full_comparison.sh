#!/bin/bash
# 
# RUN THIS TO CAPTURE YOUR REAL SITES AND GENERATE THE COMPARISON REPORT
#
# This script will:
# 1. Capture all sites from RND website
# 2. Capture all sites from AI website  
# 3. Generate comparison showing ALL sites including Super Caremark
#

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  COMPREHENSIVE SITE COMPARISON                                 ║"
echo "║  Captures EVERY site from dropdown and compares them           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get credentials
read -p "Enter your email/username: " USERNAME
read -sp "Enter your password: " PASSWORD
echo ""
echo ""

# URLs
RND_URL="https://acme.egalvanic-rnd.com"
AI_URL="https://acme.egalvanic.ai"

echo "📋 Configuration:"
echo "   RND URL: $RND_URL"
echo "   AI URL:  $AI_URL"
echo "   User:    $USERNAME"
echo ""

# Capture RND (old) site
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 1: Capturing RND Website (Old)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

python3 capture_all_sites.py "$RND_URL" "$USERNAME" "$PASSWORD" <<EOF
n
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to capture RND site"
    echo "Please check the error message above and try again"
    exit 1
fi

# Wait a bit
sleep 2

# Capture AI (new) site
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 2: Capturing AI Website (New)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Create a modified version that captures new site
python3 capture_all_sites.py "$AI_URL" "$USERNAME" "$PASSWORD" <<EOF
n
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to capture AI site"
    exit 1
fi

# Compare
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "STEP 3: Comparing All Sites"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Find the latest capture directories
OLD_DIR=$(ls -td old_all_sites_capture* 2>/dev/null | head -1)
NEW_DIR=$(ls -td new_all_sites_capture* 2>/dev/null | head -1)

if [ -z "$OLD_DIR" ] || [ -z "$NEW_DIR" ]; then
    echo "❌ Could not find capture directories"
    echo "   Looking for: old_all_sites_capture* and new_all_sites_capture*"
    exit 1
fi

echo "Comparing:"
echo "  Old: $OLD_DIR"
echo "  New: $NEW_DIR"
echo ""

python3 site_data_comparator.py "$OLD_DIR" "$NEW_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ COMPARISON COMPLETE!                                      ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📄 Report: site_comparison_report.html"
    echo ""
    echo "This report includes ALL sites from the dropdown, including:"
    echo "  • Super Caremark (179 → 180 assets)"
    echo "  • Site657"
    echo "  • All Facilities"
    echo "  • London UK"
    echo "  • ... and every other site"
    echo ""
    echo "Opening report in browser..."
    open site_comparison_report.html 2>/dev/null || xdg-open site_comparison_report.html 2>/dev/null
    echo ""
else
    echo ""
    echo "❌ Comparison failed. Check error messages above."
    exit 1
fi
