import sys
import os
import tempfile
import pytest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    os.environ['DEPLOY_ENV'] = 'testing'
    os.environ['APP_VERSION'] = '3.0.0-test'
    
    # Use temporary database for test isolation
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.environ['DB_NAME'] = db_path
    
    from ACEest_Fitness import app as flask_app, init_db
    flask_app.config.update({
        "TESTING": True,
        "DEBUG": False
    })
    
    with flask_app.app_context():
        init_db()

    yield flask_app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
