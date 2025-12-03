"""
Pytest configuration and fixtures.
"""
import pytest
import sys
import os

# Add parent directory to path so we can import app and schemas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    from app import app as flask_app

    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task storage before each test."""
    from app import tasks

    # Clear all tasks
    tasks.clear()

    # Reset next_id to 1
    import app as app_module
    app_module.next_id = 1

    yield

    # Clean up after test
    tasks.clear()
    app_module.next_id = 1


@pytest.fixture
def sample_task():
    """Factory fixture for creating sample tasks."""
    def _create_task(title="Test Task", completed=False):
        return {
            'title': title,
            'completed': completed
        }
    return _create_task


@pytest.fixture
def created_task(client, sample_task):
    """Fixture that creates a task and returns it."""
    response = client.post('/tasks', json=sample_task())
    return response.get_json()
