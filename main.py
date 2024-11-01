from fastapi import FastAPI
from mangum import Mangum

from endpoints import router as parking_router

# App Config
app = FastAPI(
    title="Parking Backend System",
    description="API for parking system",
    version="1.0.0",
)

handler = Mangum(app)

# Endpoints
app.include_router(parking_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
