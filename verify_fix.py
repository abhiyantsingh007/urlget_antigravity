import json
import os
from ultimate_migration_verification import UltimateMigrationVerifier

# Create dummy capture directories
os.makedirs("dummy_capture_old/sites/Site657", exist_ok=True)
os.makedirs("dummy_capture_new/sites/Site657", exist_ok=True)

# Create dummy data for Old Website (Site657 has 1 asset)
old_data = {
    "metadata": {"base_url": "https://acme.egalvanic-rnd.com"},
    "api_responses": [
        {
            "url": "https://acme.egalvanic-rnd.com/api/sites/overview",
            "response": {
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 1,
                        "active_sites": 1
                    }
                }
            }
        }
    ]
}

# Create dummy data for New Website (Site657 has 0 assets - CRITICAL ERROR)
new_data = {
    "metadata": {"base_url": "https://acme.egalvanic.ai"},
    "api_responses": [
        {
            "url": "https://acme.egalvanic.ai/api/sites/overview",
            "response": {
                "sites": {
                    "Site657": {
                        "name": "Site657",
                        "total_assets": 0,
                        "active_sites": 1
                    }
                }
            }
        }
    ]
}

# Save dummy data
with open("dummy_capture_old/complete_capture.json", "w") as f:
    json.dump(old_data, f)

with open("dummy_capture_new/complete_capture.json", "w") as f:
    json.dump(new_data, f)

# Run verification
verifier = UltimateMigrationVerifier("dummy_capture_old", "dummy_capture_new")

# Load data
print("Loading data...")
old_responses = verifier.load_complete_capture("dummy_capture_old")["api_responses"]
new_responses = verifier.load_complete_capture("dummy_capture_new")["api_responses"]

# Run analysis
print("Analyzing data...")
verifier.analyze_site_specific_data(old_responses, new_responses)

# Check results
print("\nChecking results for Site657...")
site_issues = verifier.results["site_analysis"]["Site657"]["issues"]
found_critical = False

for issue in site_issues:
    print(f"Issue found: {issue['type']} - {issue['description']} (Severity: {issue['severity']})")
    if issue['type'] == 'total_assets_change' and issue['severity'] == 'CRITICAL':
        found_critical = True

if found_critical:
    print("\n✅ SUCCESS: Critical data loss (1 -> 0 assets) correctly detected!")
else:
    print("\n❌ FAILURE: Critical data loss NOT detected.")

# Generate report to verify HTML output
verifier.generate_html_report(verifier.results)
