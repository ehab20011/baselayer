# PPP Loan Data Processing Project - Phase 1

This project focuses on extracting, processing, and storing Paycheck Protection Program (PPP) loan data from the Small Business Administration (SBA) website. The implementation includes automated data scraping, data cleaning, and PostgreSQL database storage.

## Project Components

### 1. Data Scraping (`scraper.py`)
- Uses Playwright for automated web scraping from the SBA website
- Navigates through multiple pages to locate and download the PPP FOIA dataset (.csv file)
- Downloads data to a specified directory with custom naming

### 2. Data Model (`models.py`)
- Implements a Pydantic model called (`PPPDataRow`) for data validation and type checking
- Handles all the fields from the csv including loan details, borrower information, and financial data
- Coded comprehensive field validation and type conversion

### 3. Data Processing and Storage (`send_to_postgres.py`)
- Manages the PostgreSQL database connections using environment variables (.env file)
- Implements batch processing for efficient data insertion into the postgresql database
- Included good error handling and logging for debugging if issues occur
- Processes data in chunks to manage memory efficiently

### 4. Database Optimization (`create_indexes.py`)
- Creates indexes for optimizing query performance for the fastAPI
- Includes indexes for:
  - Primary lookup (loan_number)
  - Common search fields (borrower_name, borrower_state)
  - Financial analysis (initial_approval_amount, forgiveness_amount)
  - Location-based queries (composite index on state, city, zip)
  - Status tracking (loan_status)

## Data Cleaning Decisions ##
### Null Value Handling
- Standardized null value representations:
  - Empty strings
  - Various text representations ('nan', 'none', 'null', 'na', 'n/a')
  - Case-insensitive matching
  - Whitespace-only strings

### Numeric Field Processing
- Round all values to 2 decimal places
- Remove commas from numeric strings
- Convert empty numeric fields to NULL
- Special handling for fields that should be integers:
  - term
  - sba_guaranty_percentage
  - jobs_reported

### Date Handling
- Support multiple date formats:
  - Primary format: "YYYY-MM-DD HH:MM:SS"
  - Alternative format: "MM/DD/YYYY"
  - Invalid dates are converted to NULL

### String Field Cleaning
- Strip leading/trailing whitespace
- Special handling for fields that should remain strings even if numeric:
  - loan_number
  - sba_office_code
  - servicing_lender_location_id
  - naics_code
  - originating_lender_location_id

### Boolean Field Processing
- Convert various representations to boolean:
  - "true", "yes", "1", "y" → True
  - Other values → False
  - Empty/NULL values preserved as NULL

### File Encoding
- Automatic encoding detection using chardet library
- Fallback to UTF-8 if no high-confidence encoding is detected
- Handles the first 100KB of the file for encoding detection

## Error Handling
- Implements comprehensive error logging
- Batch transaction management with rollback capability
- Continues processing on row-level errors
- Limits error reporting to first 5 occurrences per type
- Tracks and reports total successful insertions and errors

## Environment Setup
Required environment variables:
- DB_HOST
- DB_NAME
- DB_USER
- DB_PASSWORD

## Performance Considerations
- Implements batch processing (1000 rows)
- Uses chunked reading for memory efficiency
- Utilizes PostgreSQL's execute_batch for optimized insertions
- Strategic database indexes for query optimization

## Data Quality Assurance
- Validates all data through Pydantic models
- Enforces data types and constraints
- Maintains data integrity through database constraints
- Preserves original data when cleaning is ambiguous