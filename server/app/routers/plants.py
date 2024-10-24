from fastapi import APIRouter

from app import schemas
from app.services.plant_service import PlantService

router = APIRouter(prefix="/plants", tags=["plants"])


# Placeholder: manually create plant with known data
@router.post("/")
def create_plant(plant: schemas.Plant):
    PlantService.create_plant(plant)
    return {"message": "Plant created successfully"}


@router.delete("/{plant_id}")
def delete_plant(plant_id: str):
    PlantService.delete_plant(plant_id=plant_id)
    return {"message": "Plant deleted successfully"}

