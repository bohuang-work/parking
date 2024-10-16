import requests

# Get the endpoint URL from environment variable or use default
BASE_URL = "http://localhost:8000"
PARKING_SLOTS_ENDPOINT = BASE_URL + "/parking-slots/create"


# Initialize 100 parking slots via HTTP request
def initialize_parking_slots():
    # Payload containing parking slots to be created
    slots = [
        {"slot_number": i, "is_free": True, "license_plate": None}
        for i in range(1, 101)
    ]

    # Make POST request to create parking slots
    try:
        response = requests.post(PARKING_SLOTS_ENDPOINT, json=slots)

        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully initialized {len(slots)} parking slots.")
        elif response.status_code == 409:
            print("Parking slots already exist.")
        else:
            print(
                f"Failed to initialize parking slots. Status code: {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the parking slots API: {e}")


# Call the function to initialize parking slots
if __name__ == "__main__":
    initialize_parking_slots()
