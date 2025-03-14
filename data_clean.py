import pandas as pd
from models import PPPDataRow
from typing import List
import csv

# Define numeric fields that need special handling
numeric_fields = [
    'sba_guaranty_percentage', 'initial_approval_amount', 'current_approval_amount',
    'undisbursed_amount', 'jobs_reported', 'utilities_proceed', 'payroll_proceed',
    'mortgage_interest_proceed', 'rent_proceed', 'refinance_eidl_proceed',
    'health_care_proceed', 'debt_interest_proceed', 'forgiveness_amount'
]

def clean_ppp_data(csv_path: str, output_path: str, rows: int = 5000) -> None:
    """
    Reads and cleans the PPP dataset CSV, writing valid rows directly to output CSV.
    Arguments:
        csv_path: Path to the input CSV file
        output_path: Path to write the cleaned CSV file
        rows: Number of rows to process (Limiting it to 5000 right now for testing purposes)
    """
    #For the different types of encodings..
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    df = None
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding, nrows=rows)
            print(f"Successfully read {rows} rows with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise ValueError("Could not read the CSV file with any of the attempted encodings")

    # Clean column names to match model field names
    df.columns = [col.strip() for col in df.columns]

    # Handle all kinds of null values and the empty string
    null_values = ['nan', 'none', 'null', '', 'na', 'n/a', 'NaN', 'None', 'NULL', 'NA', 'N/A']
    df = df.replace(null_values, None)
    
    # Trim spaces from string values and convert empty strings to None
    df = df.map(lambda x: None if pd.isna(x) or (isinstance(x, str) and x.strip() in null_values) 
                else x.strip() if isinstance(x, str) 
                else x)

    # Handle numeric fields - convert to float where possible
    for field in numeric_fields:
        if field in df.columns:
            # Convert to numeric, coerce errors to NaN
            df[field] = pd.to_numeric(df[field], errors='coerce')
            # Replace NaN with None for proper SQL NULL handling
            df[field] = df[field].where(pd.notnull(df[field]), None)
            # Round to 2 decimal places for currency fields
            if field not in ['sba_guaranty_percentage', 'jobs_reported']:
                df[field] = df[field].apply(lambda x: round(float(x), 2) if x is not None else None)

    # Initialize the counters
    valid_count = 0
    invalid_count = 0
    first_error = None

    # Open output CSV file for writing
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Get the fieldnames from the model
        fieldnames = list(PPPDataRow.model_fields.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for idx, row in df.iterrows():
            try:
                # Convert row to dict and handle NaN values
                row_dict = {k: None if pd.isna(v) else v for k, v in row.to_dict().items()}
                
                # Clean the data through the Pydantic model
                validated_row = PPPDataRow(**row_dict)
                validated_dict = validated_row.model_dump()
                writer.writerow(validated_dict)
                valid_count += 1
                
                if valid_count % 1000 == 0:
                    print(f"Processed {valid_count} valid rows...")
                
            except Exception as e:
                if first_error is None:
                    first_error = (e, row_dict)
                    print("\nFirst validation error encountered:")
                    print(f"Error: {e}")
                    print("Data causing the error:")
                    for key, value in row_dict.items():
                        print(f"{key}: {value}")
                invalid_count += 1

    # Print the result
    print(f"\n✅ Successfully cleaned and wrote {valid_count} rows to {output_path}")
    print(f"❌ Skipped {invalid_count} rows due to validation errors")

if __name__ == "__main__":
    csv_file_path = "C:/Users/Ehab Abdalla/Desktop/BaseLayer/PPP_loan_dataset.csv"
    output_file_path = "cleaned_ppp_data.csv"
    clean_ppp_data(csv_file_path, output_file_path)
    print("✅ Data cleaning completed successfully!")
