import pandas as pd
from models import PPPDataRow
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import chardet
from psycopg2.extras import execute_batch

# Define numeric fields that need special handling
NUMERIC_FIELDS = {
    'term', 'sba_guaranty_percentage', 'initial_approval_amount', 'current_approval_amount',
    'undisbursed_amount', 'jobs_reported', 'utilities_proceed', 'payroll_proceed',
    'mortgage_interest_proceed', 'rent_proceed', 'refinance_eidl_proceed',
    'health_care_proceed', 'debt_interest_proceed', 'forgiveness_amount'
}

#This function establishes a connection to the PostgreSQL database using environment variables
def get_db_connection():
    """Establish a connection to the PostgreSQL database using environment variables."""
    load_dotenv()
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

#This function detects the encoding of the file using chardet and returns the best possible encoding
def detect_encoding(file_path):
    """Detect file encoding using chardet and return the best possible encoding."""
    with open(file_path, 'rb') as file:
        raw_data = file.read(100000)  # Read the first 100KB
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']

    if encoding and confidence > 0.8:
        print(f"✅ Detected encoding: {encoding} with {confidence:.2f} confidence")
        return encoding

    print("⚠️ No high-confidence encoding detected, defaulting to utf-8")
    return 'utf-8'

#This function 
def format_value(value, field_name=None):
    """Format values for PostgreSQL insertion."""
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return None
    
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    # Handle numeric fields
    if field_name in NUMERIC_FIELDS:
        try:
            if isinstance(value, str):
                value = value.strip().replace(',', '')
                if value == '':
                    return None
            return float(value)
        except (ValueError, TypeError):
            return None
            
    return value

#This array defines the expected columns for the PPP dataset
EXPECTED_COLUMNS = [
    "loan_number", "date_approved", "sba_office_code", "processing_method",
    "borrower_name", "borrower_address", "borrower_city", "borrower_state", "borrower_zip",
    "loan_status_date", "loan_status", "term", "sba_guaranty_percentage", "initial_approval_amount",
    "current_approval_amount", "undisbursed_amount", "franchise_name", "servicing_lender_location_id",
    "servicing_lender_name", "servicing_lender_address", "servicing_lender_city", "servicing_lender_state",
    "servicing_lender_zip", "rural_urban_indicator", "hubzone_indicator", "lmi_indicator",
    "business_age_description", "project_city", "project_county_name", "project_state", "project_zip",
    "cd", "jobs_reported", "naics_code", "race", "ethnicity", "utilities_proceed", "payroll_proceed",
    "mortgage_interest_proceed", "rent_proceed", "refinance_eidl_proceed", "health_care_proceed",
    "debt_interest_proceed", "business_type", "originating_lender_location_id", "originating_lender",
    "originating_lender_city", "originating_lender_state", "gender", "veteran", "non_profit",
    "forgiveness_amount", "forgiveness_date"
]

#This dictionary maps the column names to the expected columns
COLUMN_MAP = {col.replace("_", "").lower(): col for col in EXPECTED_COLUMNS}

#This function normalizes the column names for consistency so I can use it to map the columns to the expected columns
def normalize_key(key: str) -> str:
    """Normalize column names for consistency."""
    return COLUMN_MAP.get(key.replace("_", "").lower(), key)

#This function cleans the dataframe before insertion into the postgres table
def clean_dataframe(df):
    """Cleans and formats a DataFrame before insertion into PostgreSQL."""
    null_values = {'nan', 'none', 'null', '', 'na', 'n/a', 'NaN', 'None', 'NULL', 'NA', 'N/A'}

    # Strip whitespace from the column names
    df.columns = df.columns.str.strip()

    # Replace the known null values
    df.replace(null_values, None, inplace=True)

    # Apply transformations efficiently using map instead of applymap
    for column in df.columns:
        df[column] = df[column].map(
            lambda x: None if pd.isna(x) or (isinstance(x, str) and x.strip().lower() in null_values)
            else x.strip() if isinstance(x, str)
            else x
        )

    # Convert the numeric fields
    for field in NUMERIC_FIELDS:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').round(2)
    
    return df

#This function reads, cleans, and directly inserts the PPP dataset into PostgreSQL
def clean_and_insert_ppp_data(csv_path: str, batch_size: int = 1000):
    #Detect the encoding of the file
    encoding = detect_encoding(csv_path)

    #Establish a connection to the PostgreSQL database
    with get_db_connection() as conn, conn.cursor() as cur:
        print("Attempting to read the CSV file...")

        # Read the file in chunks
        chunks = pd.read_csv(csv_path, encoding=encoding, chunksize=10000, on_bad_lines='skip', low_memory=False)

        total_rows = 0
        error_count = 0
        batch = []

        #Process the file in chunks
        for chunk_num, df in enumerate(chunks, 1):
            print(f"\nProcessing chunk {chunk_num}...")

            df = clean_dataframe(df)

            for _, row in df.iterrows():
                try:
                    row_dict = {k: None if pd.isna(v) else v for k, v in row.to_dict().items()}
                    
                    # Validate and normalize data
                    validated_row = PPPDataRow(**row_dict)
                    validated_dict = validated_row.model_dump()

                    formatted_row = {normalize_key(k): format_value(v, k) for k, v in validated_dict.items()}

                    batch.append(formatted_row)

                    if len(batch) >= batch_size:
                        try:
                            execute_batch(
                                cur,
                                f"INSERT INTO ppp_loans ({', '.join(EXPECTED_COLUMNS)}) VALUES ({', '.join(['%(' + col + ')s' for col in EXPECTED_COLUMNS])})",
                                batch
                            )
                            conn.commit()
                            total_rows += len(batch)
                            print(f"✅ Successfully inserted batch. Total rows: {total_rows}")
                        except Exception as e:
                            conn.rollback()
                            error_count += len(batch)
                            print(f"❌ Error inserting batch: {e}")
                        finally:
                            batch = []

                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"\nValidation error: {e}\nData causing the error: {row_dict}")

        if batch:
            try:
                execute_batch(
                    cur,
                    f"INSERT INTO ppp_loans ({', '.join(EXPECTED_COLUMNS)}) VALUES ({', '.join(['%(' + col + ')s' for col in EXPECTED_COLUMNS])})",
                    batch
                )
                conn.commit()
                total_rows += len(batch)
                print(f"✅ Successfully inserted final batch. Total rows: {total_rows}")
            except Exception as e:
                conn.rollback()
                error_count += len(batch)
                print(f"❌ Error inserting final batch: {e}")

    print(f"\n✅ Data processing completed! {total_rows:,} rows inserted. {error_count:,} errors encountered.")

if __name__ == "__main__":
    csv_file_path = "C:/Users/Ehab Abdalla/Desktop/BaseLayer/cleaned_ppp_data.csv"
    clean_and_insert_ppp_data(csv_file_path)
    print("✅ Data cleaning and insertion completed successfully!")
