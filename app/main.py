import asyncio

from fastapi import FastAPI
from app.routers import plants, devices, weather
from app import mqtt_client, tasks

mqtt_client.start_mqtt_loop()

app = FastAPI()

app.include_router(plants.router)
app.include_router(devices.router)
app.include_router(weather.router)


@app.on_event("startup")
async def startup_event():
    # noinspection PyAsyncCall
    asyncio.create_task(tasks.fetch_forecast_periodically())
