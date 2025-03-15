import pandas as pd
from models import PPPDataRow
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import chardet
from psycopg2.extras import execute_batch
import time

# Define numeric fields that need special handling
NUMERIC_FIELDS = {
    'term', 'sba_guaranty_percentage', 'initial_approval_amount', 'current_approval_amount',
    'undisbursed_amount', 'jobs_reported', 'utilities_proceed', 'payroll_proceed',
    'mortgage_interest_proceed', 'rent_proceed', 'refinance_eidl_proceed',
    'health_care_proceed', 'debt_interest_proceed', 'forgiveness_amount'
}

def get_db_connection():
    """Establish a connection to the PostgreSQL database using environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    try:
        conn = psycopg2.connect(
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("DB_HOST", "db"),
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        raise

def detect_encoding(file_path):
    """Detect file encoding using chardet and return the best possible encoding."""
    with open(file_path, 'rb') as file:
        raw_data = file.read(100000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
    if encoding and confidence > 0.8:
        print(f"INFO: Detected encoding {encoding} with {confidence:.2f} confidence")
        return encoding
    print("WARNING: No high-confidence encoding detected, defaulting to utf-8")
    return 'utf-8'

def format_value(value, field_name=None):
    """Format values for PostgreSQL insertion."""
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return None
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
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

COLUMN_MAP = {col.replace("_", "").lower(): col for col in EXPECTED_COLUMNS}

def normalize_key(key: str) -> str:
    """Normalize column names for consistency."""
    return COLUMN_MAP.get(key.replace("_", "").lower(), key)

def clean_dataframe(df):
    """Clean and format a DataFrame before insertion into PostgreSQL."""
    null_values = {'nan', 'none', 'null', '', 'na', 'n/a', 'NaN', 'None', 'NULL', 'NA', 'N/A'}
    df.columns = df.columns.str.strip()
    df.replace(null_values, None, inplace=True)
    for column in df.columns:
        df[column] = df[column].map(
            lambda x: None if pd.isna(x) or (isinstance(x, str) and x.strip().lower() in null_values)
            else x.strip() if isinstance(x, str) else x
        )
    for field in NUMERIC_FIELDS:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors='coerce').round(2)
    return df

def read_csv_safely(file_path, chunk_size=None):
    """
    Read CSV file safely by trying multiple encodings in sequence.
    
    Args:
        file_path: Path to the CSV file
        chunk_size: Optional size for chunked reading
        
    Returns:
        DataFrame or TextFileReader for chunked reading
    """
    # List of encodings to try in order
    encodings = [
        'utf-8-sig',  # UTF-8 with BOM
        'cp1252',     # Windows-1252
        'utf-8',      # Standard UTF-8
        'latin1',     # Latin-1
        'iso-8859-1'  # Another common encoding
    ]
    
    last_error = None
    for encoding in encodings:
        try:
            print(f"INFO: Attempting to read CSV with encoding: {encoding}")
            if chunk_size:
                return pd.read_csv(
                    file_path,
                    encoding=encoding,
                    chunksize=chunk_size,
                    on_bad_lines='skip',
                    low_memory=False
                )
            return pd.read_csv(
                file_path,
                encoding=encoding,
                on_bad_lines='skip',
                low_memory=False
            )
        except Exception as e:
            last_error = e
            print(f"INFO: Failed with encoding {encoding}: {str(e)}")
            continue
    
    # If we get here, none of the encodings worked
    raise ValueError(f"Failed to read CSV file with any encoding. Last error: {last_error}")

def clean_and_insert_ppp_data(csv_path: str, batch_size: int = 1000, row_limit: int = 5000):
    """
    Clean and insert PPP data into PostgreSQL.
    Processes rows in batches, stopping after row_limit rows.
    """
    start_time = time.time()
    last_batch_time = start_time

    with get_db_connection() as conn, conn.cursor() as cur:
        print("INFO: Attempting to read the CSV file...")
        try:
            chunks = read_csv_safely(csv_path, chunk_size=batch_size)
            print("INFO: Successfully opened CSV file")
        except ValueError as e:
            print(f"ERROR: Failed reading CSV: {e}")
            return None, None

        total_rows = 0      # Total number of rows successfully inserted
        processed_rows = 0  # Total number of rows processed from the CSV
        error_count = 0
        batch = []

        # Iterate over CSV chunks
        for chunk_num, df in enumerate(chunks, 1):
            chunk_start_time = time.time()
            print(f"INFO: Processing chunk {chunk_num}...")
            df = clean_dataframe(df)
            
            # Process each row in the chunk
            for _, row in df.iterrows():
                # If we've reached the row limit, break out of both loops.
                if processed_rows >= row_limit:
                    print(f"INFO: Reached row limit of {row_limit}. Stopping further processing.")
                    break

                try:
                    row_dict = {k: None if pd.isna(v) else v for k, v in row.to_dict().items()}
                    validated_row = PPPDataRow(**row_dict)
                    validated_dict = validated_row.model_dump()
                    formatted_row = {normalize_key(k): format_value(v, k) for k, v in validated_dict.items()}
                    batch.append(formatted_row)
                    processed_rows += 1
                                        
                    if len(batch) >= batch_size:
                        try:
                            execute_batch(
                                cur,
                                f"INSERT INTO ppp_loans ({', '.join(EXPECTED_COLUMNS)}) VALUES ({', '.join(['%(' + col + ')s' for col in EXPECTED_COLUMNS])})",
                                batch
                            )
                            conn.commit()
                            total_rows += len(batch)
                            current_time = time.time()
                            batch_duration = current_time - last_batch_time
                            total_duration = current_time - start_time
                            rows_per_second = len(batch) / batch_duration
                            print(f"INFO: Batch inserted successfully. "
                                  f"Total rows inserted: {total_rows:,}. "
                                  f"Batch processing time: {batch_duration:.2f}s. "
                                  f"Rows/second this batch: {rows_per_second:.2f}. "
                                  f"Total elapsed time: {total_duration:.2f}s")
                            last_batch_time = current_time
                        except Exception as e:
                            conn.rollback()
                            error_count += len(batch)
                            print(f"ERROR: Failed inserting batch: {e}")
                        finally:
                            batch = []
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Only show first 5 validation errors
                        print(f"ERROR: Validation failed: {e}\nProblematic data: {row_dict}")

            # Check after finishing a chunk if the row limit was reached.
            if processed_rows >= row_limit:
                break

        # Insert any remaining rows in the final batch
        if batch:
            try:
                execute_batch(
                    cur,
                    f"INSERT INTO ppp_loans ({', '.join(EXPECTED_COLUMNS)}) VALUES ({', '.join(['%(' + col + ')s' for col in EXPECTED_COLUMNS])})",
                    batch
                )
                conn.commit()
                total_rows += len(batch)
                current_time = time.time()
                batch_duration = current_time - last_batch_time
                total_duration = current_time - start_time
                rows_per_second = len(batch) / batch_duration
                print(f"INFO: Final batch inserted successfully. "
                      f"Total rows inserted: {total_rows:,}. "
                      f"Batch processing time: {batch_duration:.2f}s. "
                      f"Rows/second this batch: {rows_per_second:.2f}")
            except Exception as e:
                conn.rollback()
                error_count += len(batch)
                print(f"ERROR: Failed inserting final batch: {e}")

    total_duration = time.time() - start_time
    avg_rows_per_second = total_rows / total_duration if total_duration > 0 else 0
    print(f"\nINFO: Processing completed."
          f"\n  - Total rows inserted: {total_rows:,}"
          f"\n  - Total errors: {error_count:,}"
          f"\n  - Total time: {total_duration:.2f}s"
          f"\n  - Average rows/second: {avg_rows_per_second:.2f}")
    return total_rows, error_count

if __name__ == "__main__":
    import os
    csv_file_path = os.path.join(os.path.dirname(__file__), "PPP_loan_dataset.csv")
    clean_and_insert_ppp_data(csv_file_path)
    print("INFO: Data cleaning and insertion completed")
