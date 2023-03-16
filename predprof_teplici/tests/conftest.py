import os
import pytest
from app import create_app

os.mkdir("data")

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app()

    app.config["TESTING"] = True

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
