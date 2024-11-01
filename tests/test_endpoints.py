from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db
from sqlmodel import SQLModel
import pytest
import os

# Set up the test database using SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Use a test SQLite database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
SQLModel.metadata.create_all(engine)


# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # This function can be used to set up initial data
    yield  # This is where the testing happens

    # Cleanup: remove the test database file after tests
    if os.path.exists("test.db"):
        os.remove("test.db")


# Health Check Test
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok!"}


# Test for Creating Parking Slots
def test_create_parking_slots():
    parking_slots = [
        {"slot_number": 1, "is_free": True},
        {"slot_number": 2, "is_free": True},
    ]

    response = client.post("/parking-slots/create", json=parking_slots)

    assert response.status_code == 200
    assert response.json() == {"slots_created": len(parking_slots)}


# Test for Getting Free Parking Slots
def test_get_free_parking_slots():
    response = client.get("/parking-slots/free")

    assert response.status_code == 200
    free_slots = response.json()
    assert len(free_slots) == 2  # Expecting 2 free slots
    assert all(
        slot["is_free"] is True for slot in free_slots
    )  # Ensure all returned slots are free
