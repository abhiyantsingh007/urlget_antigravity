#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced migration verification functionality
"""

import re

def extract_numeric_values_demo():
    """Demo function to show how numeric values are extracted"""
    # Sample texts simulating website content
    old_text = """
    Dashboard Overview
    Total Sites: 42
    Active Users: 127
    Assets (15)
    Pending Issues: 5
    Site657 - Total Assets: 1
    """
    
    new_text = """
    Dashboard Overview
    Total Sites: 42
    Active Users: 129
    Assets (0)
    Pending Issues: 5
    Site657 - Total Assets: 0
    New Feature Added
    """
    
    print("OLD TEXT:")
    print(old_text)
    print("\nNEW TEXT:")
    print(new_text)
    
    # Extract numeric values using the same method as in the enhanced verification
    patterns = [
        r'(?:total\s*)?assets?\s*[:\-]?\s*(\d+)',
        r'assets?\s*\((\d+)\)',
        r'count\s*[:\-]?\s*(\d+)',
        r'total\s*[:\-]?\s*(\d+)',
        r'(\d+)\s*assets?',
    ]
    
    print("\nEXTRACTED NUMERIC VALUES:")
    
    old_numbers = {}
    new_numbers = {}
    
    for pattern in patterns:
        old_matches = re.findall(pattern, old_text, re.IGNORECASE)
        new_matches = re.findall(pattern, new_text, re.IGNORECASE)
        
        for i, match in enumerate(old_matches):
            key = f"pattern_{pattern}_{i}"
            old_numbers[key] = int(match)
            
        for i, match in enumerate(new_matches):
            key = f"pattern_{pattern}_{i}"
            new_numbers[key] = int(match)
    
    print(f"Old values: {old_numbers}")
    print(f"New values: {new_numbers}")
    
    # Compare values
    print("\nCOMPARISON RESULTS:")
    all_keys = set(old_numbers.keys()) | set(new_numbers.keys())
    differences_found = False
    
    for key in all_keys:
        old_val = old_numbers.get(key, None)
        new_val = new_numbers.get(key, None)
        
        if old_val is None and new_val is not None:
            print(f"  ADDED: {key} = {new_val}")
            differences_found = True
        elif old_val is not None and new_val is None:
            print(f"  REMOVED: {key} was {old_val}")
            differences_found = True
        elif old_val is not None and new_val is not None and old_val != new_val:
            severity = "CRITICAL" if new_val == 0 and old_val > 0 else "MINOR"
            print(f"  CHANGED [{severity}]: {key} from {old_val} to {new_val}")
            differences_found = True
    
    if not differences_found:
        print("  No numeric differences found")

if __name__ == "__main__":
    print("Testing Enhanced Migration Verification - Numeric Value Detection")
    print("=" * 60)
    extract_numeric_values_demo()