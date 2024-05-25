import asyncio

from fastapi import FastAPI, Depends

from app import tasks
from app.routers import plants, devices, weather
from app.services.device_service import DeviceService

device_service = DeviceService()

app = FastAPI()

app.include_router(devices.router, dependencies=[Depends(lambda: device_service)])
app.include_router(plants.router)
app.include_router(weather.router)


@app.on_event("startup")
async def startup_event():
    # noinspection PyAsyncCall
    asyncio.create_task(tasks.fetch_forecast_periodically())
