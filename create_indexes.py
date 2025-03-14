from send_to_postgres import get_db_connection

def create_indexes():
    """Create indexes to optimize query performance for the PPP loans database."""
    
    # List of indexes to create
    indexes = [
        # Primary lookup index
        """CREATE INDEX IF NOT EXISTS idx_loan_number 
           ON ppp_loans(loan_number)""",
        
        # Common search field indexes
        """CREATE INDEX IF NOT EXISTS idx_borrower_name 
           ON ppp_loans(borrower_name)""",
        """CREATE INDEX IF NOT EXISTS idx_borrower_state 
           ON ppp_loans(borrower_state)""",
        """CREATE INDEX IF NOT EXISTS idx_date_approved 
           ON ppp_loans(date_approved)""",
        
        # Financial analysis indexes
        """CREATE INDEX IF NOT EXISTS idx_initial_approval_amount 
           ON ppp_loans(initial_approval_amount)""",
        """CREATE INDEX IF NOT EXISTS idx_forgiveness_amount 
           ON ppp_loans(forgiveness_amount)""",
        
        # Composite index for location-based queries
        """CREATE INDEX IF NOT EXISTS idx_location 
           ON ppp_loans(borrower_state, borrower_city, borrower_zip)""",
        
        # Status index
        """CREATE INDEX IF NOT EXISTS idx_loan_status 
           ON ppp_loans(loan_status)"""
    ]
    
    # Connect to database and create indexes
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for index_sql in indexes:
                try:
                    print(f"Creating index: {index_sql}")
                    cur.execute(index_sql)
                    conn.commit()
                    print("✅ Index created successfully!")
                except Exception as e:
                    print(f"❌ Error creating index: {e}")
                    conn.rollback()

if __name__ == "__main__":
    print("Creating database indexes...")
    create_indexes()
    print("Index creation completed!") 