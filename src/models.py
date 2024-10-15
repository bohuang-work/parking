from datetime import UTC, datetime
from enum import Enum
from typing import List, Optional

import sqlmodel as sm
from pydantic import BaseModel
from src.database import CarsDB, ParkingSlotsDB, TicketsDB


### 1. ParkingSlot API models
class ParkingSlotBase(BaseModel):
    slot_number: int
    is_free: bool = True
    license_plate: Optional[str] = None  # It can be null if the slot is free


# Model for creating a new Parking Slot (input)
class ParkingSlotPostRequest(ParkingSlotBase):
    pass


# Model for reading a Parking Slot (output)
class ParkingSlotGetResponse(ParkingSlotBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    tickets: Optional[List["TicketsDB"]] = None


### 2. Car API models
class CarBase(BaseModel):
    license_plate: str


# Model for creating a new User (input)
class CarPostRequest(CarBase):
    pass


# Model for reading a User (output)
class CarGetResponse(CarBase):

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    tickets: Optional[List["TicketsDB"]] = None


### 3. Ticket API models
class TicketBase(BaseModel):
    entry_time: datetime
    exit_time: Optional[datetime] = None


class TicketPostRequest(TicketBase):
    license_plate: str
    parking_slot_id: int


class TicketGetResponse(TicketBase):
    id: int
    car_id: int
    parking_slot_id: int
    paid: bool = False
