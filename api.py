from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from dotenv import load_dotenv
from send_to_postgres import get_db_connection
from pydantic import BaseModel
from datetime import datetime

# Load environment variables
load_dotenv()

# Create the FastAPI app instance
app = FastAPI(
    title="PPP Loans API",
    description="API for searching and retrieving PPP (Paycheck Protection Program) loan data",
    version="1.0.0"
)

# Response models
class BusinessSearchResponse(BaseModel):
    loan_number: str
    borrower_name: Optional[str] = None
    borrower_address: Optional[str] = None
    borrower_city: Optional[str] = None
    borrower_state: Optional[str] = None
    initial_approval_amount: Optional[float] = None
    forgiveness_amount: Optional[float] = None

class BusinessDetailsResponse(BaseModel):
    loan_number: str
    date_approved: Optional[datetime] = None
    borrower_name: Optional[str] = None
    borrower_address: Optional[str] = None
    borrower_city: Optional[str] = None
    borrower_state: Optional[str] = None
    borrower_zip: Optional[str] = None
    loan_status: Optional[str] = None
    loan_status_date: Optional[datetime] = None
    initial_approval_amount: Optional[float] = None
    current_approval_amount: Optional[float] = None
    forgiveness_amount: Optional[float] = None
    forgiveness_date: Optional[datetime] = None
    jobs_reported: Optional[int] = None
    business_type: Optional[str] = None
    business_age_description: Optional[str] = None
    naics_code: Optional[str] = None
    rural_urban_indicator: Optional[str] = None
    hubzone_indicator: Optional[bool] = None
    lmi_indicator: Optional[bool] = None
    
@app.get("/search", response_model=List[BusinessSearchResponse])
async def search_businesses(
    name: str = Query(..., description="Business name to search for"),
    borrower_state: Optional[str] = Query(None, description="Filter by borrower state (e.g., CA, NY)"),
    borrower_city: Optional[str] = Query(None, description="Filter by borrower city"),
):
    try:
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Construct the SQL query
        query = """
            SELECT 
                loan_number,
                borrower_name,
                borrower_address,
                borrower_city,
                borrower_state,
                initial_approval_amount,
                forgiveness_amount
            FROM ppp_loans
            WHERE borrower_name ILIKE %s
        """
        params = [f"%{name}%"]

        # Add optional filters per Requirements 
        if borrower_state:
            query += " AND borrower_state = %s"
            params.append(borrower_state.upper())
        if borrower_city:
            query += " AND borrower_city ILIKE %s"
            params.append(f"%{borrower_city}%")

        # Add limit and order
        query += " ORDER BY initial_approval_amount DESC LIMIT 100"

        # Execute query on the database
        cur.execute(query, params)
        results = cur.fetchall()

        # Convert results to response model
        businesses = []
        for row in results:
            business = dict(zip([
                'loan_number', 'borrower_name', 'borrower_address',
                'borrower_city', 'borrower_state', 'initial_approval_amount',
                'forgiveness_amount'
            ], row))
            businesses.append(BusinessSearchResponse(**business))

        return businesses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@app.get("/business/{loan_number}", response_model=BusinessDetailsResponse)
async def get_business_details(loan_number: str):
    try:
        # Get database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Build the SQL query
        query = """
            SELECT 
                loan_number,
                date_approved,
                borrower_name,
                borrower_address,
                borrower_city,
                borrower_state,
                borrower_zip,
                loan_status,
                loan_status_date,
                initial_approval_amount,
                current_approval_amount,
                forgiveness_amount,
                forgiveness_date,
                jobs_reported,
                business_type,
                business_age_description,
                naics_code,
                rural_urban_indicator,
                hubzone_indicator,
                lmi_indicator
            FROM ppp_loans
            WHERE loan_number = %s
        """
        
        # Execute query
        cur.execute(query, [loan_number])
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Business not found")

        # Convert result to response model
        business = dict(zip([
            'loan_number', 'date_approved', 'borrower_name',
            'borrower_address', 'borrower_city', 'borrower_state',
            'borrower_zip', 'loan_status', 'loan_status_date',
            'initial_approval_amount', 'current_approval_amount',
            'forgiveness_amount', 'forgiveness_date', 'jobs_reported',
            'business_type', 'business_age_description', 'naics_code',
            'rural_urban_indicator', 'hubzone_indicator', 'lmi_indicator'
        ], result))

        return BusinessDetailsResponse(**business)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

#Extra Endpoint: Retrieve the top 10 businesses that received the highest loan amounts
@app.get("/top-borrowers", response_model=List[BusinessSearchResponse])
async def get_top_borrowers():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                loan_number, borrower_name, borrower_address,
                borrower_city, borrower_state, initial_approval_amount,
                forgiveness_amount
            FROM ppp_loans
            ORDER BY initial_approval_amount DESC
            LIMIT 10
        """
        
        cur.execute(query)
        results = cur.fetchall()
        
        businesses = [BusinessSearchResponse(**dict(zip([
            'loan_number', 'borrower_name', 'borrower_address',
            'borrower_city', 'borrower_state', 'initial_approval_amount',
            'forgiveness_amount'
        ], row))) for row in results]
        
        return businesses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

#Returns the number of loans issued in a given state
@app.get("/loan-count/{state}", response_model=dict)
async def get_loan_count(state: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT COUNT(*)
            FROM ppp_loans
            WHERE borrower_state = %s
        """
        
        cur.execute(query, [state.upper()])
        count = cur.fetchone()[0]
        
        return {"state": state.upper(), "total_loans": count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 