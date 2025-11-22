"""
Script to run pre-migration data capture
"""

from pre_migration_capture import PreMigrationDataCapture

# Configuration - Update with actual credentials
BASE_URL = "https://acme.qa.egalvanic.ai"
EMAIL = "rahul+acme@egalvanic.com"
PASSWORD = "RP@egalvanic123"

if __name__ == "__main__":
    # Run pre-migration capture
    capture = PreMigrationDataCapture(BASE_URL, EMAIL, PASSWORD)
    output_directory = capture.run_capture()
    
    print(f"\nPre-migration capture completed!")
    print(f"All data has been saved to: {output_directory}")
    print("\nAfter the website migration, run the post_migration_capture.py script")
    print("Then use the compare_pre_post_migration function to compare the data")