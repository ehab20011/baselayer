import psycopg2
import csv
import os
from dotenv import load_dotenv
from datetime import datetime

# Define numeric fields that need special handling
NUMERIC_FIELDS = {
    'term', 'sba_guaranty_percentage', 'initial_approval_amount', 'current_approval_amount',
    'undisbursed_amount', 'jobs_reported', 'utilities_proceed', 'payroll_proceed',
    'mortgage_interest_proceed', 'rent_proceed', 'refinance_eidl_proceed',
    'health_care_proceed', 'debt_interest_proceed', 'forgiveness_amount'
}

def format_value(value, field_name=None):
    """
    Format values for PostgreSQL insertion
    Args:
        value: The value to format
        field_name: The name of the field (used to determine type)
    """
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

def insert_ppp_data(csv_file: str, batch_size: int = 100) -> None:
    """
    Insert cleaned PPP data into PostgreSQL database.
    Args:
        csv_file: Path to the cleaned CSV file
        batch_size: Number of rows to insert in each batch
    """
    # Load database connection parameters from .env file
    load_dotenv()
    
    # Configure database connection
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    
    # Set autocommit to False to handle transactions manually
    conn.autocommit = False
    cur = conn.cursor()
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            batch = []
            total_rows = 0
            error_count = 0
            
            for row in reader:
                # Format values for PostgreSQL
                formatted_row = {k: format_value(v, k) for k, v in row.items()}
                batch.append(formatted_row)
                
                if len(batch) >= batch_size:
                    try:
                        # Insert batch
                        cur.executemany(
                            """
                            INSERT INTO ppp_loans (
                                loan_number, date_approved, sba_office_code, processing_method,
                                borrower_name, borrower_address, borrower_city, borrower_state, borrower_zip,
                                loan_status_date, loan_status, term, sba_guaranty_percentage, initial_approval_amount,
                                current_approval_amount, undisbursed_amount, franchise_name, servicing_lender_location_id,
                                servicing_lender_name, servicing_lender_address, servicing_lender_city, servicing_lender_state,
                                servicing_lender_zip, rural_urban_indicator, hubzone_indicator, lmi_indicator,
                                business_age_description, project_city, project_county_name, project_state, project_zip,
                                cd, jobs_reported, naics_code, race, ethnicity, utilities_proceed, payroll_proceed,
                                mortgage_interest_proceed, rent_proceed, refinance_eidl_proceed, health_care_proceed,
                                debt_interest_proceed, business_type, originating_lender_location_id, originating_lender,
                                originating_lender_city, originating_lender_state, gender, veteran, non_profit,
                                forgiveness_amount, forgiveness_date
                            )
                            VALUES (
                                %(loan_number)s, %(date_approved)s, %(sba_office_code)s, %(processing_method)s,
                                %(borrower_name)s, %(borrower_address)s, %(borrower_city)s, %(borrower_state)s, %(borrower_zip)s,
                                %(loan_status_date)s, %(loan_status)s, %(term)s, %(sba_guaranty_percentage)s, %(initial_approval_amount)s,
                                %(current_approval_amount)s, %(undisbursed_amount)s, %(franchise_name)s, %(servicing_lender_location_id)s,
                                %(servicing_lender_name)s, %(servicing_lender_address)s, %(servicing_lender_city)s, %(servicing_lender_state)s,
                                %(servicing_lender_zip)s, %(rural_urban_indicator)s, %(hubzone_indicator)s, %(lmi_indicator)s,
                                %(business_age_description)s, %(project_city)s, %(project_county_name)s, %(project_state)s, %(project_zip)s,
                                %(cd)s, %(jobs_reported)s, %(naics_code)s, %(race)s, %(ethnicity)s, %(utilities_proceed)s, %(payroll_proceed)s,
                                %(mortgage_interest_proceed)s, %(rent_proceed)s, %(refinance_eidl_proceed)s, %(health_care_proceed)s,
                                %(debt_interest_proceed)s, %(business_type)s, %(originating_lender_location_id)s, %(originating_lender)s,
                                %(originating_lender_city)s, %(originating_lender_state)s, %(gender)s, %(veteran)s, %(non_profit)s,
                                %(forgiveness_amount)s, %(forgiveness_date)s
                            )
                            """,
                            batch
                        )
                        conn.commit()
                        total_rows += len(batch)
                        print(f"✅ Successfully inserted batch. Total rows: {total_rows}")
                        
                    except Exception as e:
                        conn.rollback()
                        error_count += len(batch)
                        print(f"❌ Error inserting batch: {str(e)}")
                        print(f"First problematic row in batch: {batch[0]}")
                    
                    finally:
                        batch = []
            
            # Insert any remaining rows
            if batch:
                try:
                    cur.executemany(
                        """
                        INSERT INTO ppp_loans (
                            loan_number, date_approved, sba_office_code, processing_method,
                            borrower_name, borrower_address, borrower_city, borrower_state, borrower_zip,
                            loan_status_date, loan_status, term, sba_guaranty_percentage, initial_approval_amount,
                            current_approval_amount, undisbursed_amount, franchise_name, servicing_lender_location_id,
                            servicing_lender_name, servicing_lender_address, servicing_lender_city, servicing_lender_state,
                            servicing_lender_zip, rural_urban_indicator, hubzone_indicator, lmi_indicator,
                            business_age_description, project_city, project_county_name, project_state, project_zip,
                            cd, jobs_reported, naics_code, race, ethnicity, utilities_proceed, payroll_proceed,
                            mortgage_interest_proceed, rent_proceed, refinance_eidl_proceed, health_care_proceed,
                            debt_interest_proceed, business_type, originating_lender_location_id, originating_lender,
                            originating_lender_city, originating_lender_state, gender, veteran, non_profit,
                            forgiveness_amount, forgiveness_date
                        )
                        VALUES (
                            %(loan_number)s, %(date_approved)s, %(sba_office_code)s, %(processing_method)s,
                            %(borrower_name)s, %(borrower_address)s, %(borrower_city)s, %(borrower_state)s, %(borrower_zip)s,
                            %(loan_status_date)s, %(loan_status)s, %(term)s, %(sba_guaranty_percentage)s, %(initial_approval_amount)s,
                            %(current_approval_amount)s, %(undisbursed_amount)s, %(franchise_name)s, %(servicing_lender_location_id)s,
                            %(servicing_lender_name)s, %(servicing_lender_address)s, %(servicing_lender_city)s, %(servicing_lender_state)s,
                            %(servicing_lender_zip)s, %(rural_urban_indicator)s, %(hubzone_indicator)s, %(lmi_indicator)s,
                            %(business_age_description)s, %(project_city)s, %(project_county_name)s, %(project_state)s, %(project_zip)s,
                            %(cd)s, %(jobs_reported)s, %(naics_code)s, %(race)s, %(ethnicity)s, %(utilities_proceed)s, %(payroll_proceed)s,
                            %(mortgage_interest_proceed)s, %(rent_proceed)s, %(refinance_eidl_proceed)s, %(health_care_proceed)s,
                            %(debt_interest_proceed)s, %(business_type)s, %(originating_lender_location_id)s, %(originating_lender)s,
                            %(originating_lender_city)s, %(originating_lender_state)s, %(gender)s, %(veteran)s, %(non_profit)s,
                            %(forgiveness_amount)s, %(forgiveness_date)s
                        )
                        """,
                        batch
                    )
                    conn.commit()
                    total_rows += len(batch)
                    print(f"✅ Successfully inserted final batch. Total rows: {total_rows}")
                    
                except Exception as e:
                    conn.rollback()
                    error_count += len(batch)
                    print(f"❌ Error inserting final batch: {str(e)}")
                    print(f"First problematic row in batch: {batch[0]}")
    
    finally:
        cur.close()
        conn.close()
        
    print(f"\n✅ Data insertion completed!")
    print(f"Successfully inserted {total_rows} rows")
    print(f"❌ Encountered {error_count} errors")

if __name__ == "__main__":
    csv_file = "cleaned_ppp_data.csv"
    insert_ppp_data(csv_file)
    print("✅ Database insertion completed successfully!")
