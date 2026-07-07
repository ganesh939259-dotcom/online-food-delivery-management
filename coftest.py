import os
import pytest

os.environ.setdefault("ACCOUNT_SID", "AC" + "0"*32)
os.environ.setdefault("AUTH_TOKEN", "0"*32)
os.environ.setdefault("TWILIO_NUMBER", "+10000000000")

from app import app as flask_app, db

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with flask_app.app_context():
        db.create_all()

    with flask_app.test_client() as client:
        yield client

    with flask_app.app_context():
        db.drop_all()