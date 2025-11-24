"""
Script to run the enhanced site data capture
This version captures data for all sites in the dropdown, not just ShowSite3
"""

from enhanced_site_capture import run_enhanced_capture

if __name__ == "__main__":
    print("Starting enhanced site data capture...")
    print("This script will capture data for ALL sites in the dropdown, including:")
    print("- London UK")
    print("- All Facilities") 
    print("- Melbourne AU")
    print("- ShowSite3")
    print("- test")
    print("- test site")
    print("- Toronto Canada")
    print("")
    print("Using URL: https://acme.egalvanic.ai")
    print("")
    
    run_enhanced_capture()