# PPP Loan Data Processing Project - Phase 1

This project focuses on extracting, processing, and storing Paycheck Protection Program (PPP) loan data from the Small Business Administration (SBA) website. The implementation includes automated data scraping, robust data cleaning, and efficient PostgreSQL database storage.

## Project Components

### 1. Data Scraping (`scraper.py`)
- Utilizes Playwright for automated web scraping from the SBA website
- Navigates through multiple pages to locate and download the PPP FOIA dataset
- Downloads data to a specified directory with custom naming

### 2. Data Model (`models.py`)
- Implements a Pydantic model (`PPPDataRow`) for data validation and type checking
- Handles 50+ fields including loan details, borrower information, and financial data
- Includes comprehensive field validation and type conversion

### 3. Data Processing and Storage (`send_to_postgres.py`)
- Manages PostgreSQL database connections using environment variables
- Implements batch processing for efficient data insertion
- Includes robust error handling and logging
- Processes data in chunks to manage memory efficiently

### 4. Database Optimization (`create_indexes.py`)
- Creates strategic indexes for optimizing query performance
- Includes indexes for:
  - Primary lookup (loan_number)
  - Common search fields (borrower_name, borrower_state)
  - Financial analysis (initial_approval_amount, forgiveness_amount)
  - Location-based queries (composite index on state, city, zip)
  - Status tracking (loan_status)

## Data Cleaning Decisions

### Null Value Handling
- Standardized null value representations including:
  - Empty strings
  - Various text representations ('nan', 'none', 'null', 'na', 'n/a')
  - Case-insensitive matching
  - Whitespace-only strings

### Numeric Field Processing
- Round all monetary values to 2 decimal places
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
- Automatic encoding detection using chardet
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
- Implements batch processing (default batch size: 1000 rows)
- Uses chunked reading for memory efficiency
- Utilizes PostgreSQL's execute_batch for optimized insertions
- Strategic database indexes for query optimization

## Data Quality Assurance
- Validates all data through Pydantic models
- Enforces data types and constraints
- Maintains data integrity through database constraints
- Preserves original data when cleaning is ambiguous

## Next Steps
- Implement data analysis queries
- Create visualization layer
- Add monitoring for data quality
- Implement regular data refresh mechanism 