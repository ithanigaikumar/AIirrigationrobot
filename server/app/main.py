import asyncio

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app import tasks
from app.routers import plants, devices, weather
from app.services.device_service import DeviceService

# handles MQTT client connection
device_service = DeviceService()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router, dependencies=[Depends(lambda: device_service)])
app.include_router(plants.router)
app.include_router(weather.router)


@app.on_event("startup")
async def startup_event():
    # noinspection PyAsyncCall
    asyncio.create_task(tasks.fetch_forecast_periodically())
