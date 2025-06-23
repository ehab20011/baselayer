#!/bin/bash

set -e

echo "Starting PPP Loan Data processing..."

# Check if ppp_csvs directory exists
if [ ! -d "ppp_csvs" ]; then
    echo "ppp_csvs directory not found. Creating it..."
    mkdir -p ppp_csvs
fi

# Check if both CSV files exist
if [ ! -f "ppp_csvs/ppp.csv" ] || [ ! -f "ppp_csvs/ppp_subset.csv" ]; then
    echo "CSV files not found. Starting data download and processing..."
    
    # Run playwright.py to download the CSV file
    echo "Downloading PPP loan data..."
    python playwright.py
    
    # Check if the download was successful
    if [ -f "ppp_csvs/PPP_loan_dataset.csv" ]; then
        echo "Download successful. Renaming file to ppp.csv..."
        mv ppp_csvs/PPP_loan_dataset.csv ppp_csvs/ppp.csv
    else
        echo "Error: Download failed. File not found."
        exit 1
    fi
    
    # Run subset.py to create the subset
    echo "Creating subset of the data..."
    python subset.py
    
    echo "Data processing completed successfully!"
else
    echo "CSV files already exist. Skipping download and processing."
    
    # Wait for database to be ready
    echo "Waiting for database to be ready..."
    sleep 10
    
    # Run the data processing pipeline
    echo "Starting PPP loan data processing pipeline..."
    python run.py
    
    echo "Pipeline execution completed!"
fi

# Wait for Postgres to be ready for FastAPI
DB_CHECK_CMD="import psycopg2; psycopg2.connect(dbname='${DB_NAME}', user='${DB_USER}', password='${DB_PASSWORD}', host='${DB_HOST}', port='${DB_PORT}')"
echo "Waiting for Postgres to be ready for FastAPI..."
until python -c "$DB_CHECK_CMD"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done
echo "Postgres is up - starting FastAPI server"

# Launch the FastAPI server
echo "Starting FastAPI server..."
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Keep the container running for debugging or additional processing
echo "Container is ready. You can now run additional commands or start your application."
tail -f /dev/null 