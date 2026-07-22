from datetime import datetime
import os
from fastapi import APIRouter, Depends, status , HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.pipeline_service import PipelineService
from app.schemas.drone import DroneRecordRead
from app.models.drone import DroneRecord

#API Endpoints Drones
router = APIRouter()

INPUT_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../../data/drone_records.json")

@router.get("/drones", response_model=list[DroneRecordRead])
def get_drones_records(
    drone_type: str | None = None,
    status: str | None = None,
    operator_id: str | None = None,
    min_battery: int | None = None,
    max_battery: int | None = None,
    from_date: datetime | None = None,  
    to_date: datetime | None = None,
    db: Session = Depends(get_db) ,
    drone_id : str | None = None , 
    page: int=1,
    page_size: int=5
):
    if page < 1:
        page = 1
    query = db.query(DroneRecord)
    if drone_type is not None:
        query = query.filter(DroneRecord.drone_type == drone_type)

    if status is not None:
        query = query.filter(DroneRecord.status == status)

    if operator_id is not None:
        query = query.filter(DroneRecord.operator_id == operator_id)


    if min_battery is not None:
        query = query.filter(DroneRecord.battery_percent >= min_battery)
    if max_battery is not None:
        query = query.filter(DroneRecord.battery_percent <= max_battery)

    if from_date is not None:
        query = query.filter(DroneRecord.timestamp >= from_date)

    if to_date is not None:
        query = query.filter(DroneRecord.timestamp <= to_date)
    
    if drone_id is not None:
        query = query.filter(DroneRecord.drone_id == drone_id)

    offset_value = (page - 1) * page_size
    query = query.offset(offset_value).limit(page_size)

    print(str(query))

    result = query.all()

    return result

@router.get("/drones/{id}", response_model=DroneRecordRead)
def get_single_drone(id: int , db: Session = Depends(get_db)):
    drone = db.query(DroneRecord).filter(DroneRecord.id == id).first()
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drone

# @router.delete("/drones/{id}")
# def delete_single_drone(id: int , db: Session = Depends(get_db)):
#     drone = db.query(DroneRecord).filter(DroneRecord.id == id).first()
#     if not drone:
#         raise HTTPException(status_code=404, detail="Drone not found")
#     db.delete(drone)
#     db.commit()
#     return {"message": "Drone deleted successfully"}

# @router.get("/drones/by_operator/{operator_id}", response_model=list[DroneRecordRead])
# def get_drone_by_op(operator_id: str  , db: Session = Depends(get_db)):
#     drone = db.query(DroneRecord).filter(DroneRecord.operator_id == operator_id).all()
#     if not drone:
#         raise HTTPException(status_code=404, detail="Drone not found")
#     return drone


# @router.put("/drones/{id}/battery", response_model=DroneRecordRead)
# def put_battery_precent(id: int ,new_battery: int , db: Session = Depends(get_db)):
#     drone = db.query(DroneRecord).filter(DroneRecord.id == id).first()
#     if not drone:
#         raise HTTPException(status_code=404, detail="Drone not found")
    
#     drone.battery_percent = new_battery
#     db.commit()
#     return drone