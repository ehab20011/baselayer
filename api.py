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
    hubzone_indicator: Optional[str] = None
    lmi_indicator: Optional[str] = None
    
@app.get("/search", response_model=List[BusinessSearchResponse])
async def search_businesses(
    name: str = Query(..., description="Business name to search for"),
    state: Optional[str] = Query(None, description="Filter by state (e.g., CA, NY)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    min_amount: Optional[float] = Query(None, description="Minimum initial approval amount"),
    max_amount: Optional[float] = Query(None, description="Maximum initial approval amount")
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
        if state:
            query += " AND borrower_state = %s"
            params.append(state.upper())
        if city:
            query += " AND borrower_city ILIKE %s"
            params.append(f"%{city}%")
        if min_amount is not None:
            query += " AND initial_approval_amount >= %s"
            params.append(min_amount)
        if max_amount is not None:
            query += " AND initial_approval_amount <= %s"
            params.append(max_amount)

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

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 