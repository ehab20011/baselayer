import pytest
from fastapi.testclient import TestClient
from api import app
import psycopg2
from send_to_postgres import get_db_connection

client = TestClient(app)

#TESTS
def get_sample_loan_number():
    """Get a real loan number from the database for testing."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT loan_number FROM ppp_loans LIMIT 1")
    loan_number = cur.fetchone()[0]
    cur.close()
    conn.close()
    return loan_number

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search_businesses():
    """Test the business search endpoint."""
    # Get a real business name from the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT borrower_name, borrower_state, borrower_city FROM ppp_loans LIMIT 1")
    business = cur.fetchone()
    cur.close()
    conn.close()
    
    business_name = business[0]
    business_state = business[1]
    business_city = business[2]

    # Test with just name
    response = client.get(f"/search?name={business_name}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

    # Test with name and state
    response = client.get(f"/search?name={business_name}&borrower_state={business_state}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Test with name and city
    response = client.get(f"/search?name={business_name}&borrower_city={business_city}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Test with invalid parameters
    response = client.get("/search")
    assert response.status_code == 422  # Validation error

def test_get_business_details():
    """Test the business details endpoint."""
    # Get a real loan number from the database
    loan_number = get_sample_loan_number()
    
    response = client.get(f"/business/{loan_number}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["loan_number"] == loan_number
    assert "borrower_name" in data
    assert "initial_approval_amount" in data

    # Test non-existent loan number
    response = client.get("/business/nonexistent123")
    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"

def test_top_borrowers():
    """Test the top borrowers endpoint."""
    response = client.get("/top-borrowers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10  # Should return at most 10 results

    if len(data) > 0:
        # Verify the structure of returned data
        first_item = data[0]
        assert "loan_number" in first_item
        assert "borrower_name" in first_item
        assert "initial_approval_amount" in first_item

        # Verify the results are ordered by initial_approval_amount in descending order
        if len(data) > 1:
            amounts = [float(item["initial_approval_amount"] or 0) for item in data]
            assert all(amounts[i] >= amounts[i+1] for i in range(len(amounts)-1))

def test_invalid_routes():
    """Test invalid routes return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404