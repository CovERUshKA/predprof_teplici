import pytest

from predprof_teplici import create_app

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
