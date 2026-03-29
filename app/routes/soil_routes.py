from fastapi import APIRouter
from ..models import CropInput
from ..services.soil_service import insert_soil_data, get_latest_soil_data, get_all_soil_data

from fastapi import APIRouter
from app.services import soil_service

router = APIRouter(prefix="/soildata")


@router.post("/insert")
def create_soil_data(input: CropInput):
    return insert_soil_data(input.dict())

@router.get("/latest")
def read_latest():
    return soil_service.get_latest_soil_data()

@router.get("/all")
def read_all():
    return soil_service.get_all_soil_data()
