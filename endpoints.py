import math
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import CarsDB, ParkingSlotsDB, TicketsDB, get_db
from models import (
    CarGetResponse,
    CarPostRequest,
    ParkingSlotGetResponse,
    ParkingSlotPostRequest,
    TicketGetResponse,
    TicketPostRequest,
)

# Create an APIRouter instance
router = APIRouter()


# Health Check Endpoint
@router.get("/", tags=["Health"])
def health_check():
    return {"status": "ok!"}


# Parking Slot Endpoints
@router.post("/parking-slots/create", response_model=dict, tags=["Parking Slots"])
def create_parking_slots(
    parking_slots: List[ParkingSlotPostRequest], db: Session = Depends(get_db)
):
    new_slots = []

    for parking_slot_data in parking_slots:
        # Create a new ParkingSlot object from the input data
        new_slot: ParkingSlotsDB = ParkingSlotsDB(**parking_slot_data.model_dump())
        db.add(new_slot)
        new_slots.append(new_slot)

    db.commit()

    # Return the number of parking slots created
    return {"slots_created": len(new_slots)}


@router.get(
    "/parking-slots/free",
    response_model=List[ParkingSlotGetResponse],
    tags=["Parking Slots"],
)
def get_free_parking_slots(db: Session = Depends(get_db)):
    free_slots = db.query(ParkingSlotsDB).filter(ParkingSlotsDB.is_free == True).all()

    if not free_slots:
        raise HTTPException(status_code=404, detail="No free parking slots available")

    return free_slots


@router.get(
    "/parking-slots/free/count",
    response_model=int,
    tags=["Parking Slots"],
)
def get_number_of_free_parking_slots(db: Session = Depends(get_db)):
    free_slots_count = (
        db.query(ParkingSlotsDB).filter(ParkingSlotsDB.is_free == True).count()
    )

    return free_slots_count


@router.get(
    "/parking-slots/{slot_id}",
    response_model=ParkingSlotGetResponse,
    tags=["Parking Slots"],
)
def get_parking_slot_by_id(slot_id: int, db: Session = Depends(get_db)):
    parking_slot = db.query(ParkingSlotsDB).filter(ParkingSlotsDB.id == slot_id).first()

    if not parking_slot:
        raise HTTPException(status_code=404, detail="Parking slot not found")

    return parking_slot


# Car Endpoints
@router.post("/cars/create", response_model=dict, tags=["Cars"])
def create_car(car: CarPostRequest, db: Session = Depends(get_db)):
    # check if the car already exists by license plate
    if db.query(CarsDB).filter(CarsDB.license_plate == car.license_plate).first():
        return {"message": "Car already exists"}
    else:
        new_car: CarsDB = CarsDB(**car.model_dump())
        db.add(new_car)
        db.commit()

        return {"message": "Car created successfully"}


@router.get(
    "/cars/{license_plate}",
    response_model=CarGetResponse,
    tags=["Cars"],
)
def get_car_by_license_plate(license_plate: str, db: Session = Depends(get_db)):
    car = db.query(CarsDB).filter(CarsDB.license_plate == license_plate).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


# Ticket Endpoints
@router.post("/tickets/create", response_model=dict, tags=["Tickets"])
def create_ticket(ticket: TicketPostRequest, db: Session = Depends(get_db)):
    # Check if the parking slot is free
    parking_slot = (
        db.query(ParkingSlotsDB)
        .filter(ParkingSlotsDB.id == ticket.parking_slot_id)
        .first()
    )
    if not parking_slot or not parking_slot.is_free:
        raise HTTPException(status_code=400, detail="Parking slot is not free")

    # Find the car id by license plate
    car = db.query(CarsDB).filter(CarsDB.license_plate == ticket.license_plate).first()
    if not car:
        raise HTTPException(
            status_code=404, detail="Car not registered, please register the car first"
        )

    # Create a new Ticket object
    new_ticket: TicketsDB = TicketsDB(
        car_id=car.id,
        parking_slot_id=ticket.parking_slot_id,
        entry_time=(
            ticket.entry_time if ticket.entry_time else datetime.now(timezone.utc)
        ),
        exit_time=ticket.exit_time if ticket.exit_time else None,
    )
    db.add(new_ticket)

    # Update the parking slot to be occupied
    parking_slot.is_free = False
    parking_slot.license_plate = ticket.license_plate
    db.commit()

    return {
        "message": f"Ticket created successfully, ticket id: {new_ticket.id}, car parked at slot: {parking_slot.slot_number}"
    }


# Endpoint to get a ticket by ID
@router.get("/tickets/{ticket_id}", response_model=TicketGetResponse, tags=["Tickets"])
def get_ticket_by_id(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketsDB).filter(TicketsDB.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


# Endpoint to pay for a ticket
@router.put("/tickets/pay/{ticket_id}", response_model=dict, tags=["Tickets"])
def pay_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketsDB).filter(TicketsDB.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # check if the ticket has already been paid
    if ticket.paid:
        return {"message": "Ticket has already been paid"}

    # Update the ticket with the exit time
    if ticket.exit_time is None:
        ticket.exit_time = datetime.now(timezone.utc)
        db.commit()

    # Update the parking slot to be free
    parking_slot = (
        db.query(ParkingSlotsDB)
        .filter(ParkingSlotsDB.id == ticket.parking_slot_id)
        .first()
    )
    parking_slot.is_free = True
    parking_slot.license_plate = None
    db.commit()

    # calculate the total time spent in the parking
    total_hours = math.ceil(
        (ticket.exit_time - ticket.entry_time).total_seconds() / 3600
    )
    price = total_hours * 5

    # update ticket as paid
    ticket.paid = True
    db.commit()

    return {"message": "Ticket paid successfully", "Price": f"{price} Euro"}


# Endpoint to cancel a ticket
@router.delete("/tickets/cancel/{ticket_id}", response_model=dict, tags=["Tickets"])
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(TicketsDB).filter(TicketsDB.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Update the parking slot to be free
    parking_slot = (
        db.query(ParkingSlotsDB)
        .filter(ParkingSlotsDB.id == ticket.parking_slot_id)
        .first()
    )
    parking_slot.is_free = True
    parking_slot.license_plate = None
    db.commit()

    # Delete the ticket
    db.delete(ticket)
    db.commit()

    return {"message": "Ticket canceled successfully"}
