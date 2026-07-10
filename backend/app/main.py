
import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.db.database import Base, engine, get_db
from app.services.pipeline_service import PipelineService
from app.routers import drones, pipeline

Base.metadata.create_all(bind=engine)
INPUT_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/drone_records.json")

app = FastAPI(
    title="Drone Activity Map Dashboard API",
    version="0.1.0"
)


app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(drones.router, prefix="/api", tags=["Drones"]) 


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def test_pipeline(db: Session = Depends(get_db)):

    result = PipelineService.run_ingestion_pipeline(db, INPUT_FILE_PATH)
    return result
