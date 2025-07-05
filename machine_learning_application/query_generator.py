import os
import psycopg2
import logging
from dotenv import load_dotenv
import requests
from typing import Any
import time

# set up the schema that will be passed into gpt
SCHEMA: str = """
    Table: ppp_loan_data_airflow
    Columns:
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(), the id of the loan
                loan_number TEXT NOT NULL, the loan number
                date_approved TIMESTAMP NOT NULL, the date the loan was approved
                borrower_name TEXT NOT NULL, the name of the borrower
                sba_office_code TEXT, the SBA office code
                processing_method TEXT, the method of processing the loan
                borrower_address TEXT, the address of the borrower
                borrower_city TEXT, the city of the borrower
                borrower_state TEXT, the state of the borrower
                borrower_zip TEXT, the zip code of the borrower
                loan_status_date TIMESTAMP, the date the loan status was updated
                loan_status TEXT, the status of the loan
                term INTEGER, the term of the loan
                sba_guaranty_percentage FLOAT, the SBA guaranty percentage
                initial_approval_amount FLOAT, the initial approval amount
                current_approval_amount FLOAT, the current approval amount
                undisbursed_amount FLOAT, the undisbursed amount
                franchise_name TEXT, the name of the franchise
                servicing_lender_location_id TEXT, the location id of the servicing lender
                servicing_lender_name TEXT, the name of the servicing lender
                servicing_lender_address TEXT, the address of the servicing lender
                servicing_lender_city TEXT, the city of the servicing lender
                servicing_lender_state TEXT, the state of the servicing lender
                servicing_lender_zip TEXT, the zip code of the servicing lender
                rural_urban_indicator TEXT, the rural/urban indicator
                hubzone_indicator TEXT, the hubzone indicator
                lmi_indicator TEXT, the lmi indicator
                business_age_description TEXT, the business age description
                project_city TEXT, the city of the project
                project_county_name TEXT, the county name of the project
                project_state TEXT, the state of the project
                project_zip TEXT, the zip code of the project
                cd TEXT, the cd of the project
                jobs_reported INTEGER, the number of jobs reported
                naics_code TEXT, the naics code of the project
                race TEXT, the race of the borrower
                ethnicity TEXT, the ethnicity of the borrower
                utilities_proceed FLOAT, the utilities proceed
                payroll_proceed FLOAT, the payroll proceed
                mortgage_interest_proceed FLOAT, the mortgage interest proceed
                rent_proceed FLOAT, the rent proceed
                refinance_eidl_proceed FLOAT, the refinance eidl proceed
                health_care_proceed FLOAT, the health care proceed
                debt_interest_proceed FLOAT, the debt interest proceed
                business_type TEXT, the business type
                originating_lender_location_id TEXT, the location id of the originating lender 
                originating_lender TEXT, the name of the originating lender
                originating_lender_city TEXT, the city of the originating lender
                originating_lender_state TEXT, the state of the originating lender
                gender TEXT, the gender of the borrower
                veteran TEXT, the veteran status of the borrower
                non_profit TEXT, the non-profit status of the borrower
                forgiveness_amount FLOAT, the forgiveness amount
                forgiveness_date TIMESTAMP, the forgiveness date
                shard_id BIGINT, the shard id
        """
# set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ensure that database is connected
def connect_to_database() -> psycopg2.extensions.connection:
    try:
        db_config = {
            "dbname":   os.getenv("DB_NAME"),
            "user":     os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host":     os.getenv("DB_HOST", "localhost"),
            "port":     os.getenv("DB_PORT", "5432"),
        }
        conn: psycopg2.extensions.connection = psycopg2.connect(**db_config)

        # return the connection
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

# function that takes a natural language question and returns a sql query
def generate_query(question: str) -> str:
    question: str = question.lower()

    # schema of the table with information on each column to help ChatGPT understand the table
    table_schema: str = SCHEMA
    
    # create the prompt for ChatGPT
    prompt = f"""
    Given this PostgreSQL table schema:
    {table_schema}

    Generate a PostgreSQL query to answer this question: "{question}"

    Requirements:
    1. Return ONLY the SQL query, no explanations
    2. Use proper PostgreSQL syntax (not MySQL or other databases)
    3. For ROUND function with decimals, use ROUND(value::numeric, 2) syntax
    4. Limit results to 1000 rows maximum with LIMIT clause
    5. Handle NULL values appropriately
    6. Use PostgreSQL-specific functions and syntax
    7. For aggregations, cast to numeric before rounding: ROUND(AVG(column)::numeric, 2)
    8. For business name searches, always use ILIKE with wildcards (%) for partial matching
       Example: WHERE borrower_name ILIKE '%company name%'

    PostgreSQL Query:
    """

    try:
        # Get API key from the environment variables
        api_key: str = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # OpenAI API endpoint
        url: str = "https://api.openai.com/v1/chat/completions"
        
        # API Headers
        headers: dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # prepare the request data payload
        data: dict[str, Any] = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a PostgreSQL expert. Respond only with the PostgreSQL query using correct PostgreSQL syntax."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0
        }
        
        # make the POST request to the OpenAI API
        response: requests.Response = requests.post(url, headers=headers, json=data)
        
        # check if the request was successful, if it was, extract the SQL query from the response
        if response.status_code == 200:
            result: dict[str, Any] = response.json()
            sql_query: str = result['choices'][0]['message']['content'].replace('```sql', '').replace('```', '').strip()

            # remove any leading/trailing whitespace or newlines
            sql_query = sql_query.strip()

            # log the SQL query
            logger.info(f"SQL Query: {sql_query} \n")

            # return the SQL query
            return sql_query
        
        # if the request was not successful, raise an exception
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"Error generating query: {str(e)}")
        raise

# function that queries the database with the sql query generated by LLM
def query_database(sql_query: str) -> list[tuple]:
    try:
        # connect to database
        conn: psycopg2.extensions.connection = connect_to_database()
        if conn is None:
            raise Exception("Failed to connect to database")
        logger.info("✅ Connected to database successfully. Going to execute the query now.\n")

        # execute the query
        cursor: psycopg2.extensions.cursor = conn.cursor()
        cursor.execute(sql_query)
        result: list[tuple] = cursor.fetchall()

        # close the cursor and connection
        cursor.close()
        conn.close()

        return result

    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        raise

# function that generates a response to the question
def generate_response(result: list[tuple], question: str) -> str:
    try:
        # Get API key from the environment variables
        api_key: str = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Create the prompt for ChatGPT to format the response
        prompt = f"""
        Question: {question}

        Raw Database Results:
        {result[:10]}  # Show first 10 results for context

        Requirements:
        1. Provide a clear, natural language summary of the results
        2. Format numbers with appropriate commas and decimal places
        3. If relevant, mention the total count of results
        4. If showing money values, use proper currency formatting ($)
        5. Keep the response concise but informative
        6. If no results, explain that no data was found

        Please format a response that answers the original question using this data.
        """

        # OpenAI API endpoint
        url: str = "https://api.openai.com/v1/chat/completions"
        
        # API Headers
        headers: dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # prepare the request data payload
        data: dict[str, Any] = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that explains database results clearly and concisely."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7  # Allow some creativity in response formatting
        }
        
        # make the POST request to the OpenAI API
        response: requests.Response = requests.post(url, headers=headers, json=data)
        
        # check if the request was successful
        if response.status_code == 200:
            result_data: dict[str, Any] = response.json()
            formatted_response: str = result_data['choices'][0]['message']['content'].strip()
            
            return formatted_response
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return f"Error formatting response: {str(e)}"

# main function
if __name__ == "__main__":
    # load environment variables
    load_dotenv()

    # connect to database
    connection: psycopg2.extensions.connection = connect_to_database()
    if connection is None:
        raise Exception("Failed to connect to database")
    logger.info("✅ Connected to database successfully \n")

    # sleep for 3 seconds
    logger.info(f"Going to sleep for 3 seconds now and then try querying the database with your question")
    time.sleep(3)

    # get the question from the frontend
    question: str = "Who is the business with the longest who had their loan status approval take the longest time?"
    logger.info(f"Question: {question} \n")

    # generate the query
    postgres_sql_query: str = generate_query(question)
    logger.info(f"PostgreSQL Query generated by the LLM: {postgres_sql_query} \n")

    # query the database
    result: list[tuple] = query_database(postgres_sql_query)
    logger.info(f"Result: {result} \n")

    # generate a nice response to send back to the user
    response: str = generate_response(result, question)
    logger.info(f"Response generated by the LLM: {response} \n")