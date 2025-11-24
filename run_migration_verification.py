"""
Script to run the migration verification
This script verifies that all data has been correctly migrated from the old website
to the new migration website (https://acme.egalvanic.ai)
"""

from migration_verification import run_migration_verification

if __name__ == "__main__":
    print("Starting migration verification...")
    print("This script will verify that all data has been correctly migrated")
    print("from the old website to the new migration website.")
    print("")
    print("Old website: https://acme.egalvanic-rnd.com")
    print("New website: https://acme.egalvanic.ai")
    print("")
    
    run_migration_verification()