import psycopg2
import os
from dotenv import load_dotenv
import logging
import json
from typing import List, Dict, Any

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# load environment variables
load_dotenv('../.env')

# database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': 'localhost',  # using localhost since we're connecting to dockerized DB
    'port': '5434'       # port from docker-compose
}

def format_loan_text(loan: Dict[str, Any]) -> str:
    """
    Convert loan data into a natural language description.
    This text will be used for creating embeddings.
    """
    # Handle location formatting
    city = loan['borrower_city'] if loan['borrower_city'] and loan['borrower_city'] != 'N/A' else None
    state = loan['borrower_state'] if loan['borrower_state'] and loan['borrower_state'] != 'N/A' else None
    
    location = ""
    if city and state:
        location = f"in {city}, {state}"
    elif city:
        location = f"in {city}"
    elif state:
        location = f"in {state}"
    else:
        location = "(location not specified)"

    text = f"""
    {loan['borrower_name']} received a PPP loan of ${loan['initial_approval_amount']:,.2f}. 
    The business is located {location} 
    and the loan was processed by {loan['originating_lender']}. 
    """
    
    if loan['forgiveness_amount']:
        text += f"The loan was forgiven for ${loan['forgiveness_amount']:,.2f}. "
    
    if loan['borrower_industry'] and loan['borrower_industry'] != 'N/A':
        text += f"The business operates in the {loan['borrower_industry']} industry. "
    
    return text.strip()

def extract_data_from_postgres() -> List[Dict[str, Any]]:
    """
    Extract PPP loan data from PostgreSQL and format it for RAG.
    Returns a list of dictionaries with 'text' and 'metadata' fields.
    """
    try:
        # connect to the database
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # query to get loan data
        query = """
        SELECT 
            loan_number,
            borrower_name,
            borrower_address,
            NULLIF(borrower_city, 'N/A') as borrower_city,
            NULLIF(borrower_state, 'N/A') as borrower_state,
            borrower_zip,
            initial_approval_amount,
            forgiveness_amount,
            originating_lender,
            naics_code as borrower_industry
        FROM ppp_loan_data_airflow
        WHERE borrower_name IS NOT NULL
        """
        
        logger.info("Executing query to fetch loan data...")
        cursor.execute(query)
        
        # fetch all rows
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        # format data for RAG
        formatted_data = []
        for row in rows:
            # convert row to dictionary
            loan_data = dict(zip(column_names, row))
            
            # create location string for metadata
            city = loan_data['borrower_city'] if loan_data['borrower_city'] else None
            state = loan_data['borrower_state'] if loan_data['borrower_state'] else None
            location = f"{city}, {state}" if city and state else (city or state or "Location not specified")
            
            # create the document format needed for RAG
            document = {
                "text": format_loan_text(loan_data),  # natural language description
                "metadata": {
                    "loan_number": loan_data['loan_number'],
                    "borrower_name": loan_data['borrower_name'],
                    "borrower_location": location,
                    "initial_amount": float(loan_data['initial_approval_amount']) if loan_data['initial_approval_amount'] else 0,
                    "forgiveness_amount": float(loan_data['forgiveness_amount']) if loan_data['forgiveness_amount'] else 0,
                    "lender": loan_data['originating_lender'],
                    "industry": loan_data['borrower_industry']
                }
            }
            formatted_data.append(document)
        
        logger.info(f"Successfully extracted {len(formatted_data)} loan records")
        
        # save a sample to verify the format
        sample_size = min(5, len(formatted_data))
        with open('../data/processed/sample_data.json', 'w') as f:
            json.dump(formatted_data[:sample_size], f, indent=2)
        logger.info(f"Saved {sample_size} sample records to data/processed/sample_data.json")
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        raise
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # create processed data directory if it doesn't exist
    os.makedirs('../data/processed', exist_ok=True)
    
    # extract and format the data
    formatted_data = extract_data_from_postgres()
    
    # print a sample record
    if formatted_data:
        logger.info("\nSample formatted record:")
        logger.info(json.dumps(formatted_data[0], indent=2))