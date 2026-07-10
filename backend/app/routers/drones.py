import os
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.pipeline_service import PipelineService
from app.schemas.pipeline import DroneRecordRead
from app.models.pipeline import DroneRecord

#API Endpoints Drones
router = APIRouter()

INPUT_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../../data/drone_records.json")

@router.get("/drones", response_model=list[DroneRecordRead])
def get_drones_records(db: Session = Depends(get_db)):
    result = db.query(DroneRecord).all() 
    return result


@router.get("/drone/{id}", response_model=DroneRecordRead)
def get_single_drone(id: int):
      drone = db.query(DroneRecord).filter(DroneRecord.id == id).first()
    return drone

