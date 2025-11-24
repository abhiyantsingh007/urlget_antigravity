#!/bin/bash
#
# CAPTURE BOTH WEBSITES AND COMPARE
# Uses manual browser capture for reliability
#

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  TWO-WEBSITE COMPARISON CAPTURE                                  ║"
echo "║  RND vs AI Website                                               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Websites to compare:"
echo "   RND (Old): https://acme.egalvanic-rnd.com"
echo "   AI (New):  https://acme.egalvanic.ai"
echo ""

# Instructions
cat << 'EOF'

Since automated capture had issues, here's the MANUAL capture process:

╔══════════════════════════════════════════════════════════════════╗
║  STEP 1: CAPTURE RND WEBSITE                                     ║
╚══════════════════════════════════════════════════════════════════╝

1. Open Chrome and go to: https://acme.egalvanic-rnd.com
2. Log in with: rahul+acme@egalvanic.com / RP@egalvanic123
3. Open DevTools (F12) → Go to Network tab
4. Navigate through all sites in the dashboard
5. In Network tab, find API calls like:
   - /api/users/.../slds
   - /api/lookup/site-overview/...
   - /api/dashboard/...
6. For each site (especially Super Caremark):
   - Select the site
   - Find the API response in Network tab
   - Right-click → Copy → Copy Response
   - Save to a text file

OR use the automated script below...

╔══════════════════════════════════════════════════════════════════╗
║  AUTOMATED APPROACH                                              ║
╚══════════════════════════════════════════════════════════════════╝

We can try a Python script that uses authenticated requests if you can 
provide the authentication token from your browser.

Press Enter to continue with automated approach, or Ctrl+C to do manual...
EOF

read -p ""

echo ""
echo "Starting automated capture..."
echo ""

# Use curl with session cookies
cat > capture_with_curl.sh << 'SCRIPT'
#!/bin/bash

# This script will be customized based on your session
# For now, it's a template

echo "To use this approach:"
echo "1. Log into https://acme.egalvanic-rnd.com in Chrome"
echo "2. Open DevTools → Application → Cookies"
echo "3. Copy all cookies"
echo "4. We'll use them to make API calls"
echo ""
echo "This is more reliable than Selenium!"

SCRIPT

chmod +x capture_with_curl.sh

EOF

# Make executable
chmod +x capture_both_websites.sh
