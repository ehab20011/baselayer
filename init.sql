-- Create the ppp_loans table [For Docker Instance]
CREATE TABLE IF NOT EXISTS ppp_loans (
    loan_number VARCHAR(255) PRIMARY KEY,
    date_approved TIMESTAMP,
    sba_office_code VARCHAR(50),
    processing_method VARCHAR(50),
    borrower_name VARCHAR(255),
    borrower_address VARCHAR(255),
    borrower_city VARCHAR(100),
    borrower_state VARCHAR(2),
    borrower_zip VARCHAR(10),
    loan_status_date TIMESTAMP,
    loan_status VARCHAR(50),
    term INTEGER,
    sba_guaranty_percentage INTEGER,
    initial_approval_amount DECIMAL(15,2),
    current_approval_amount DECIMAL(15,2),
    undisbursed_amount DECIMAL(15,2),
    franchise_name VARCHAR(255),
    servicing_lender_location_id VARCHAR(50),
    servicing_lender_name VARCHAR(255),
    servicing_lender_address VARCHAR(255),
    servicing_lender_city VARCHAR(100),
    servicing_lender_state VARCHAR(2),
    servicing_lender_zip VARCHAR(10),
    rural_urban_indicator VARCHAR(1),
    hubzone_indicator BOOLEAN,
    lmi_indicator BOOLEAN,
    business_age_description VARCHAR(50),
    project_city VARCHAR(100),
    project_county_name VARCHAR(100),
    project_state VARCHAR(2),
    project_zip VARCHAR(10),
    cd VARCHAR(50),
    jobs_reported INTEGER,
    naics_code VARCHAR(10),
    race VARCHAR(50),
    ethnicity VARCHAR(50),
    utilities_proceed DECIMAL(15,2),
    payroll_proceed DECIMAL(15,2),
    mortgage_interest_proceed DECIMAL(15,2),
    rent_proceed DECIMAL(15,2),
    refinance_eidl_proceed DECIMAL(15,2),
    health_care_proceed DECIMAL(15,2),
    debt_interest_proceed DECIMAL(15,2),
    business_type VARCHAR(50),
    originating_lender_location_id VARCHAR(50),
    originating_lender VARCHAR(255),
    originating_lender_city VARCHAR(100),
    originating_lender_state VARCHAR(2),
    gender VARCHAR(50),
    veteran VARCHAR(50),
    non_profit BOOLEAN,
    forgiveness_amount DECIMAL(15,2),
    forgiveness_date TIMESTAMP
);

-- Create indexes for better query performance as per project requirements
CREATE INDEX IF NOT EXISTS idx_borrower_name ON ppp_loans(borrower_name);
CREATE INDEX IF NOT EXISTS idx_borrower_state ON ppp_loans(borrower_state);
CREATE INDEX IF NOT EXISTS idx_initial_approval_amount ON ppp_loans(initial_approval_amount);
CREATE INDEX IF NOT EXISTS idx_forgiveness_amount ON ppp_loans(forgiveness_amount);
CREATE INDEX IF NOT EXISTS idx_location ON ppp_loans(borrower_state, borrower_city, borrower_zip);
CREATE INDEX IF NOT EXISTS idx_loan_status ON ppp_loans(loan_status);