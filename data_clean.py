import pandas as pd
from models import PPPDataRow
from typing import List
import csv

#Function to clean the PPP dataset CSV against the Pydantic model
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

    # Convert all the columns to string type first
    df = df.astype(str)
    
    # Handle all kinds of null values and the empty string
    df = df.replace({
        'nan': None,
        'None': None,
        'NULL': None,
        '': None,
        'NaN': None,
        'null': None,
        'NULL': None
    })

    # Trim spaces from string values
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Initialize the counters
    valid_count = 0
    invalid_count = 0
    first_error = None

    # Open output CSV file for writing
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        # Get the fieldnames from the first valid row
        fieldnames = None
        
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            try:
                validated_row = PPPDataRow(**row_dict)
                validated_dict = validated_row.model_dump()
                
                # Set fieldnames from first valid row
                if fieldnames is None:
                    fieldnames = list(validated_dict.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                writer.writerow(validated_dict)
                valid_count += 1
                
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
    print(f"Successfully cleaned and wrote {valid_count} rows to {output_path}")
    print(f"Skipped {invalid_count} rows due to validation errors")

if __name__ == "__main__":
    csv_file_path = "C:/Users/Ehab Abdalla/Desktop/BaseLayer/PPP_loan_dataset.csv"
    output_file_path = "cleaned_ppp_data.csv"
    clean_ppp_data(csv_file_path, output_file_path)
    print("✅ Data cleaning completed successfully!")
