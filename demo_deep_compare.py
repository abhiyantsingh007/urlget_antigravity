#!/usr/bin/env python3
"""
DEMO DEEP ASSET COMPARISON
Shows what the deep comparison report looks like.
"""

def compare_asset_lists(old_assets, new_assets):
    print("\n" + "="*80)
    print("ASSET COMPARISON RESULTS: Super Caremark")
    print("="*80)
    
    # Create maps for easy lookup
    old_map = {a.get('name', 'Unknown'): a for a in old_assets}
    new_map = {a.get('name', 'Unknown'): a for a in new_assets}
    
    old_names = set(old_map.keys())
    new_names = set(new_map.keys())
    
    missing = old_names - new_names
    added = new_names - old_names
    common = old_names & new_names
    
    print(f"📊 Old Count: {len(old_names)}")
    print(f"📊 New Count: {len(new_names)}")
    print(f"❌ Missing Assets: {len(missing)}")
    print(f"➕ Added Assets: {len(added)}")
    
    if missing:
        print("\n🔴 MISSING ASSETS (Present in Old, Missing in New):")
        for name in sorted(missing):
            print(f"  - {name}")
            
    if added:
        print("\n🟢 ADDED ASSETS (New in New, Missing in Old):")
        for name in sorted(added):
            print(f"  + {name}")
            # Show details
            asset = new_map[name]
            print(f"    Type: {asset.get('type')}")
            print(f"    Status: {asset.get('status')}")
            print(f"    Value: ${asset.get('value', 0):,}")
            
    # Check details of common assets
    print("\n🔍 Checking details of common assets...")
    diffs = 0
    for name in common:
        old = old_map[name]
        new = new_map[name]
        
        # Compare specific fields
        fields_to_check = ['status', 'value', 'location']
        for field in fields_to_check:
            v1 = old.get(field)
            v2 = new.get(field)
            if v1 != v2:
                print(f"  ⚠️  {name}: {field} changed '{v1}' -> '{v2}'")
                diffs += 1
                
    if diffs == 0:
        print("  ✅ No detail differences found in common assets")

def main():
    # Generate 179 assets for old
    old_assets = []
    for i in range(1, 180):
        old_assets.append({
            'name': f'Asset-{i:03d}',
            'type': 'Equipment',
            'status': 'Active',
            'value': 1000,
            'location': 'Building A'
        })
        
    # Generate 180 assets for new (same + 1 new one)
    import copy
    new_assets = copy.deepcopy(old_assets) # Deep copy
    
    # Add the new one
    new_assets.append({
        'name': 'MRI Scanner X-2000',
        'type': 'Medical Imaging',
        'status': 'Installing',
        'value': 450000,
        'location': 'Radiology Wing'
    })
    
    # Simulate a change in an existing one
    new_assets[0]['status'] = 'Maintenance' # Asset-001 changed status
    
    compare_asset_lists(old_assets, new_assets)

if __name__ == "__main__":
    main()
