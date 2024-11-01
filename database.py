import os
from datetime import UTC, datetime
from enum import Enum

import sqlmodel as sm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# ### 1 .Local
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"  # Using SQLite for simplicity
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

### 2. AWS
# Use environment variables to get the database connection URL
DB_USERNAME = os.getenv("DB_USERNAME", "dbadmin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "adminAdmin123!")  # Update this to your password
DB_ENDPOINT = os.getenv(
    "DB_ENDPOINT", "your-rds-endpoint"
)  # Change this to your RDS endpoint
DB_NAME = os.getenv("DB_NAME", "parkingdb")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ENDPOINT}:5432/{DB_NAME}"
)

# Set up the database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

### 3. Set up Local Session
# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### Database Models
class ParkingSlotType(Enum):
    small = "small"
    medium = "medium"
    large = "large"
    disability = "disability"


class ParkingSlotsDB(sm.SQLModel, table=True):
    __tablename__ = "parking_slots"

    id: int = sm.Field(primary_key=True, nullable=False)
    slot_number: int = sm.Field(nullable=False)
    is_free: bool = sm.Field(default=True)
    license_plate: str | None = sm.Field(
        nullable=True, description="Link to the user/car occupying it"
    )

    created_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    updated_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    deleted_at: datetime | None = sm.Field(default=None)

    # Relationship to tickets (One-to-Many)
    tickets: list["TicketsDB"] = sm.Relationship(back_populates="parking_slot")


class CarsDB(sm.SQLModel, table=True):
    __tablename__ = "cars"

    id: int = sm.Field(primary_key=True, nullable=False)
    license_plate: str = sm.Field(unique=True, nullable=False)

    created_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    updated_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    deleted_at: datetime | None = sm.Field(default=None)

    # Relationship to tickets (One-to-Many)
    tickets: list["TicketsDB"] = sm.Relationship(back_populates="car")


class TicketsDB(sm.SQLModel, table=True):
    __tablename__ = "tickets"

    id: int = sm.Field(primary_key=True, nullable=False)
    entry_time: datetime = sm.Field(default=datetime.now(tz=UTC))
    exit_time: datetime | None = sm.Field(default=None)
    paid: bool = sm.Field(default=False)

    # Foreign key to CarsDB
    car_id: int = sm.Field(foreign_key="cars.id")  # Add foreign key
    car: "CarsDB" = sm.Relationship(back_populates="tickets")

    # Foreign key to ParkingSlotsDB
    parking_slot_id: int = sm.Field(foreign_key="parking_slots.id")  # Add foreign key
    parking_slot: "ParkingSlotsDB" = sm.Relationship(back_populates="tickets")

    created_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    updated_at: datetime | None = sm.Field(default=datetime.now(tz=UTC))
    deleted_at: datetime | None = sm.Field(default=None)


# Create the database tables
SQLModel.metadata.create_all(engine)
