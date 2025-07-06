import os
import psycopg2
import pytest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

@pytest.fixture
def db_config() -> dict[str, str]:
    """Database configuration fixture"""
    return {
        "dbname":   os.getenv("DB_NAME"),
        "user":     os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host":     os.getenv("DB_HOST", "localhost"),
        "port":     os.getenv("DB_PORT", "5432"),
    }

def test_database_connection(db_config: dict[str, str]):
    """Test that we can connect to the database"""
    try:
        # Try to connect
        conn: psycopg2.extensions.connection = psycopg2.connect(**db_config)
        cursor: psycopg2.extensions.cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        # Assertions
        assert conn is not None, "Database connection should not be None"
        assert version is not None, "Database version should not be None"
        assert len(version) > 0, "Database version should contain information"
        
        print("✅ Connected to database successfully.")
        print("PostgreSQL version:", version[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        pytest.fail(f"Failed to connect to the database: {str(e)}")

def test_database_query(db_config: dict[str, str]):
    """Test that we can execute a simple query"""
    try:
        conn: psycopg2.extensions.connection = psycopg2.connect(**db_config)
        cursor: psycopg2.extensions.cursor = conn.cursor()
        
        # Test a simple query
        cursor.execute("SELECT 1 as test_value;")
        result = cursor.fetchone()
        
        assert result is not None, "Query result should not be None"
        assert result[0] == 1, "Query should return the expected value"
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        pytest.fail(f"Failed to execute database query: {str(e)}")
