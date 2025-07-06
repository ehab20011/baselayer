import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from datetime import date
from fastapi.testclient import TestClient
from typing import Any

from server import app, PPPLoanData, Base, engine
from models import QuestionRequest

# Setup test database and client
@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# make a test client
@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# test loan data:
@pytest.fixture
def test_loan_data() -> dict[str, Any]:
    return {
        "LoanNumber": "9547507704",
        "DateApproved": "05/01/2020",
        "BorrowerName": "SUMTER COATINGS, INC.",
        "SBAOfficeCode": "0464",
        "ProcessingMethod": "PPP",
        "BorrowerAddress": "2410 Highway 15 South",
        "BorrowerCity": "Sumter",
        "BorrowerState": "SC",
        "BorrowerZip": "29150-9662",
        "LoanStatusDate": "12/18/2020",
        "LoanStatus": "Paid in Full",
        "Term": 24,
        "SBAGuarantyPercentage": 100.0,
        "InitialApprovalAmount": 773553.37,
        "CurrentApprovalAmount": 773553.37,
        "UndisbursedAmount": 0.0,
    }

# test the health check endpoint

# test the get loans endpoint


# Test get loans endpoint


# Test search by borrower name


# Test search by loan number


# Test search by date range

# Test search by forgiveness amount


# Test top borrowers endpoint


# Test ask question endpoint

