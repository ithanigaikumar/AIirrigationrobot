from fastapi import APIRouter

from app import schemas
from app.services.plant_service import PlantService

router = APIRouter(prefix="/plants", tags=["plants"])


# Placeholder: manually create plant with known data
@router.post("/")
def create_plant(plant: schemas.PlantCreate):
    PlantService.create_plant(
        plant_id=plant.plant_id,
        name=plant.name,
        light=plant.light,
        temperature=plant.temperature,
        moisture=plant.moisture
    )
    return {"message": "Plant created successfully"}


@router.delete("/{plant_id}")
def delete_plant(plant_id: str):
    PlantService.delete_plant(plant_id=plant_id)
    return {"message": "Plant deleted successfully"}
