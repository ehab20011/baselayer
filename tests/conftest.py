import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import asyncio
from typing import Generator
from api import app
from asgi_lifespan import LifespanManager

# Configure the testing ENVIRONMENT 
# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Test the postgres database URL
TEST_POSTGRES_URL = "postgresql://postgres:Baselayerproject123@db:5432/ppp_database"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_app():
    """Create a test instance of the FastAPI application."""
    async with LifespanManager(app):
        yield app

@pytest.fixture(scope="session")
async def client(test_app) -> Generator:
    """Create a test client for making requests."""
    async with TestClient(test_app) as client:
        yield client