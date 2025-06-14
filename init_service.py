import subprocess
import time
import os
from scraper import scrape_ppp_loan_data
from send_to_postgres import clean_and_insert_ppp_data

#This script will first wait for the postgresSQL database to be ready
#Then it will download the PPP data and load it into the database
def wait_for_postgres():
    """Wait for PostgreSQL to be ready"""
    max_retries = 30
    retry = 0
    while retry < max_retries:
        try:
            subprocess.run(
                ["pg_isready", "-h", "db", "-U", "postgres"],
                check=True,
                capture_output=True
            )
            print("PostgreSQL connection established")
            return True
        except subprocess.CalledProcessError:
            print(f"Attempting to connect to PostgreSQL... (attempt {retry + 1}/{max_retries})")
            retry += 1
            time.sleep(2)
    return False

def main():
    print("Starting initialization process")
    
    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        print("ERROR: PostgreSQL connection timeout")
        return 1

    # Step 1: Download the PPP data
    print("Downloading PPP data...")
    csv_path = scrape_ppp_loan_data()
    
    if not csv_path or not os.path.exists(csv_path):
        print("ERROR: Failed to download PPP data")
        return 1

    # Step 2: Clean and load data (limited to however many rows you specify)
    print("Loading data into PostgreSQL...")
    try:
        clean_and_insert_ppp_data(csv_path, row_limit=5000)
        print("Successfully loaded data into PostgreSQL")
        return 0
    except Exception as e:
        print(f"ERROR: Failed to load data into PostgreSQL: {e}")
        return 1

if __name__ == "__main__":
    exit(main())