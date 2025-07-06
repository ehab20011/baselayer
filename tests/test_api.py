import os
import pytest
import logging
import pytest_asyncio

from typing import Any, List
from datetime import datetime
from dotenv import load_dotenv
from models import DATE_FORMATS
from httpx import (
    AsyncClient,
    ASGITransport,
    Response,
)

# setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# load the environment variables
load_dotenv()

# ensure the test points at the local Postgres container
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5434"

# now import the app, Base, and engine
from server import (
    PPPLoanData,
    app,
    Base,
    engine,
    async_session,
)
from models import PPPLoanDataSchema

# setup test database and client
@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Dispose the engine to clear connection pool tied to the current event loop.
    await engine.dispose()

# make a test client
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
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
@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response: Response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test get loans endpoint
@pytest.mark.asyncio
async def test_get_loans(async_client: AsyncClient, test_loan_data: dict[str, Any], insert_test_loan):
    # The loan record is inserted via the insert_test_loan fixture
    response: Response = await async_client.get("/loans")
    try:
        assert response.status_code == 200
        data: List[PPPLoanDataSchema] = response.json()
        loan_data: PPPLoanDataSchema = data[0]
        assert len(data) == 1
        assert loan_data["LoanNumber"] == test_loan_data["LoanNumber"]
        assert loan_data["LoanStatus"] == test_loan_data["LoanStatus"]
        assert loan_data["Term"] == test_loan_data["Term"]
        assert loan_data["SBAGuarantyPercentage"] == test_loan_data["SBAGuarantyPercentage"]
        assert loan_data["InitialApprovalAmount"] == test_loan_data["InitialApprovalAmount"]
        assert loan_data["CurrentApprovalAmount"] == test_loan_data["CurrentApprovalAmount"]
        assert loan_data["UndisbursedAmount"] == test_loan_data["UndisbursedAmount"]
    except Exception as e:
        logging.error(f"\nResponse JSON: {response.json()}")
        logging.error(f"\nValidation Error Details: {str(e)}")
        raise

# Test search by borrower name
@pytest.mark.asyncio
async def test_search_by_borrower(async_client: AsyncClient, test_loan_data: dict[str, Any], insert_test_loan):
    response: Response = await async_client.get(f"/loans/search/by-borrower?borrower_name={test_loan_data['BorrowerName']}")
    assert response.status_code == 200
    data: List[PPPLoanDataSchema] = response.json()
    assert len(data) == 1
    assert data[0]["BorrowerName"] == test_loan_data["BorrowerName"]

# Test search by loan number
@pytest.mark.asyncio
async def test_search_by_loan_number(async_client: AsyncClient, test_loan_data: dict[str, Any], insert_test_loan):
    response: Response = await async_client.get(f"/loans/search/by-loan-number?loan_number={test_loan_data['LoanNumber']}")
    assert response.status_code == 200
    data: PPPLoanDataSchema = response.json()
    assert data["LoanNumber"] == test_loan_data["LoanNumber"]

###########################
#  API HELPER FUNCTIONS   #
###########################

# This fixture inserts the sample loan into the database so any test that
# needs pre-populated data can simply depend on it.  This keeps our tests
# DRY and avoids having to repeat the insertion logic in every test.
if "%Y-%m-%d" not in DATE_FORMATS:
    DATE_FORMATS.append("%Y-%m-%d")

@pytest_asyncio.fixture
async def insert_test_loan(test_loan_data: dict[str, Any]):
    """Insert a single test loan record into the database."""
    async with async_session() as session:
        # Convert string dates to datetime.date objects because the database stores dates as datetime.date objects
        date_approved = datetime.strptime(test_loan_data["DateApproved"], "%m/%d/%Y").date()
        loan_status_date = datetime.strptime(test_loan_data["LoanStatusDate"], "%m/%d/%Y").date()

        loan: PPPLoanData = PPPLoanData(
            loan_number=test_loan_data["LoanNumber"],
            date_approved=date_approved,
            borrower_name=test_loan_data["BorrowerName"],
            sba_office_code=test_loan_data["SBAOfficeCode"],
            processing_method=test_loan_data["ProcessingMethod"],
            borrower_address=test_loan_data["BorrowerAddress"],
            borrower_city=test_loan_data["BorrowerCity"],
            borrower_state=test_loan_data["BorrowerState"],
            borrower_zip=test_loan_data["BorrowerZip"],
            loan_status_date=loan_status_date,
            loan_status=test_loan_data["LoanStatus"],
            term=test_loan_data["Term"],
            sba_guaranty_percentage=test_loan_data["SBAGuarantyPercentage"],
            initial_approval_amount=test_loan_data["InitialApprovalAmount"],
            current_approval_amount=test_loan_data["CurrentApprovalAmount"],
            undisbursed_amount=test_loan_data["UndisbursedAmount"],
        )
        session.add(loan)
        await session.commit()