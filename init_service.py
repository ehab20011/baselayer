import subprocess
import time
import os
from scraper import scrape_ppp_data
from send_to_postgres import clean_and_insert_ppp_data
import uvicorn
from api import app

#This script will first wait for the postgresSQL database to be ready
#Then it will download the PPP data and load it into the database
#And finally it will start the FastAPI application
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
        return

    # Step 1: Download the PPP data
    print("Downloading PPP data...")
    csv_path = scrape_ppp_data()
    
    if not csv_path or not os.path.exists(csv_path):
        print("ERROR: Failed to download PPP data")
        return

    # Step 2: Clean and load data (limited to 5000 rows)
    print("Loading data into PostgreSQL...")
    try:
        clean_and_insert_ppp_data(csv_path, row_limit=5000)
        print("Successfully loaded data into PostgreSQL")
    except Exception as e:
        print(f"ERROR: Failed to load data into PostgreSQL: {e}")
        return

    # Step 3: Start the FastAPI application
    print("Starting FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 