# Manual Capture Instructions for Super Caremark

Since the automated site dropdown detection isn't working, here's how to manually capture **Super Caremark** data:

## Method 1: Using Browser DevTools (Recommended)

### For RND Website (179 assets):

1. **Open RND website** in Chrome/Firefox:
   ```
   https://acme.egalvanic-rnd.com
   ```

2. **Log in** with:
   - Email: rahul+acme@egalvanic.com
   - Password: RP@egalvanic123

3. **Open DevTools** (F12 or Right-click → Inspect)

4. **Go to Network tab** in DevTools

5. **Select "Super Caremark"** from the site dropdown

6. **Look for API calls** in Network tab that load after selecting Super Caremark
   - Look for calls to `/api/` endpoints
   - Common ones: `/api/lookup/site-overview/`, `/api/sld/`, `/api/dashboard/`

7. **For each API call:**
   - Click on it
   - Go to "Response" tab
   - Copy the JSON response

8. **Save the data:**
   Create a file: `manual_rnd_super_caremark.json`
   ```json
   {
     "api_responses": [{
       "url": "the_api_url_you_found",
       "response": {
         ... paste the JSON response here ...
       }
     }]
   }
   ```

### For AI Website (180 assets):

Repeat the same steps for:
```
https://acme.qa.egalvanic.ai
```

Save as: `manual_ai_super_caremark.json`

### Then Compare:

```bash
python3 site_data_comparator.py manual_rnd_super_caremark.json manual_ai_super_caremark.json
```

## Method 2: Quick Manual Entry

If you can see the numbers on screen, just create files manually:

**manual_rnd_super_caremark.json:**
```json
{
  "api_responses": [{
    "url": "https://acme.egalvanic-rnd.com/dashboard",
    "response": {
      "sites": {
        "Super Caremark": {
          "name": "Super Caremark",
          "total_assets": 179,
          "open_issues": 0,
          "active_sessions": 0
        }
      }
    }
  }]
}
```

**manual_ai_super_caremark.json:**
```json
{
  "api_responses": [{
    "url": "https://acme.qa.egalvanic.ai/dashboard",
    "response": {
      "sites": {
        "Super Caremark": {
          "name": "Super Caremark",
          "total_assets": 180,
          "open_issues": 0,
          "active_sessions": 0
        }
      }
    }
  }]
}
```

Then run:
```bash
python3 site_data_comparator.py manual_rnd_super_caremark.json manual_ai_super_caremark.json
open site_comparison_report.html
```

## Method 3: Tell Me the Page Structure

If you can:
1. Take a screenshot of the page showing Super Caremark
2. Right-click on the site selector and "Inspect Element"
3. Tell me the HTML structure/CSS selector

I can update the capture_all_sites.py script to work with your specific page layout.

## Quick Test

Want to see what the report looks like with Super Caremark? Run this:

```bash
cd /Users/vishwa/Downloads/Scupltsoft/urlget_antigravity

# Create test data
cat > test_rnd.json << 'EOF'
{"api_responses": [{"url": "test", "response": {"sites": {"Super Caremark": {"name": "Super Caremark", "total_assets": 179}}}}]}
EOF

cat > test_ai.json << 'EOF'
{"api_responses": [{"url": "test", "response": {"sites": {"Super Caremark": {"name": "Super Caremark", "total_assets": 180}}}}]}
EOF

# Create directories
mkdir -p test_rnd test_ai
mv test_rnd.json test_rnd/complete_capture.json
mv test_ai.json test_ai/complete_capture.json

# Compare
python3 site_data_comparator.py test_rnd test_ai

# View
open site_comparison_report.html
```

This will show you **exactly** what the Super Caremark comparison will look like!
