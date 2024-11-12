import os
from datetime import UTC, datetime
from enum import Enum

import sqlmodel as sm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Define the environment variable to determine the database environment
DATABASE_ENV = os.getenv("DATABASE_ENV", "local")  # Default to "local"

if DATABASE_ENV == "local":
    # Local SQLite database configuration
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"  # Using SQLite for simplicity
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # AWS PostgreSQL database configuration using environment variables
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv(
        "POSTGRES_PASSWORD", "adminAdmin123!"
    )  # Update this to your password
    POSTGRES_HOST = os.getenv(
        "POSTGRES_HOST", "postgres"
    )  # Change this to your RDS endpoint
    POSTGRES_DB = os.getenv("POSTGRES_DB", "parkingdb")

    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
