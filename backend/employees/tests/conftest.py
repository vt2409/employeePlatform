"""
Shared pytest configuration and fixtures for the employees app tests.
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Fixture providing an APIClient instance for each test."""
    return APIClient()


@pytest.fixture
def authenticated_client():
    """Fixture providing an authenticated APIClient (for future use with auth)."""
    client = APIClient()
    # TODO: Add authentication setup when auth is implemented
    return client


@pytest.fixture(autouse=True)
def reset_sequences():
    """
    Reset factory sequences between tests to ensure consistent test data names.
    """
    from employees.tests.factories import EmployeeFactory
    EmployeeFactory.reset_sequence()
    yield
    EmployeeFactory.reset_sequence()


# Markers for organizing tests
def pytest_configure(config):
    """Register custom markers for test organization."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as testing API endpoints"
    )
