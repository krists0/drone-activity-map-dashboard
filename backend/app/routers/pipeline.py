import os
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.pipeline_service import PipelineService
from app.schemas.pipeline import PipelineRunRead
from app.models.pipeline import PipelineRun
#API Endpoints
router = APIRouter()

INPUT_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../../data/drone_records.json")

@router.post("/run", status_code=status.HTTP_200_OK)
def trigger_pipeline(db: Session = Depends(get_db)) -> dict:
    result = PipelineService.run_ingestion_pipeline(db, INPUT_FILE_PATH)
    return result


@router.get("/runs", response_model=list[PipelineRunRead])
def get_pipeline_runs(db: Session = Depends(get_db)):
    runs = db.query(PipelineRun).order_by(PipelineRun.id.desc()).all()
    return runs