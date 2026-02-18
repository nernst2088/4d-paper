import pytest
from fastapi.testclient import TestClient
from src.api.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def test_paper_id():
    return "test_paper_001"

@pytest.fixture(scope="session")
def test_user_id():
    return "test_user_001"