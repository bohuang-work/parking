from src.database import ParkingSlotsDB, SessionLocal


# Initialize 100 parking slots
def initialize_parking_slots():
    with SessionLocal() as db:
        # Check if parking slots already exist
        existing_slots = db.query(ParkingSlotsDB).count()
        if existing_slots == 0:
            # Create 100 parking slots
            slots = [ParkingSlotsDB(slot_number=i, is_free=True) for i in range(1, 101)]
            db.add_all(slots)
            db.commit()
            print(f"Initialized {len(slots)} parking slots.")
        else:
            print(f"{existing_slots} parking slots already exist.")


# Call the function to initialize parking slots
if __name__ == "__main__":
    initialize_parking_slots()