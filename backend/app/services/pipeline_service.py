import json
import os
from datetime import datetime, timezone  
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.pipeline import PipelineRun
from app.models.drone import DroneRecord
from app.schemas.drone import DroneRecordBase


class PipelineService:
    @staticmethod
    def run_ingestion_pipeline(db: Session, file_path: str) -> dict:
       
        # [6] Save pipeline run status and processing counters.
        pipeline_run = PipelineRun( status="started", started_at=datetime.now(timezone.utc))
        db.add(pipeline_run)
        db.commit()

        try:
            # Check if file exists before loading
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found at: {file_path}")
            # [1] Load raw drone records
            with open(file_path, "r", encoding="utf-8") as file:
                raw_record = json.load(file)

            pipeline_run.total_records = len(raw_record)
            db.commit()

            valid_records_to_save = []
            pipeline_run.valid_records = 0
            pipeline_run.invalid_records = 0

            if not isinstance(raw_record, list):
                    raise ValueError("Input JSON must be a list of drone records")

            for record in raw_record:
                
                try:
                    #[2] Validate required fields and allowed values
                    #[4] Normalize data where needed 
                    validated_json = DroneRecordBase(**record)
                    drone_db_record = DroneRecord(
                        drone_id=validated_json.drone_id,
                        drone_type=validated_json.drone_type,
                        operator_id=validated_json.operator_id,
                        latitude=validated_json.latitude,
                        longitude=validated_json.longitude,
                        altitude_m=validated_json.altitude_m,
                        speed_kmh=validated_json.speed_kmh,
                        battery_percent=validated_json.battery_percent,
                        timestamp=validated_json.timestamp,
                        status=validated_json.status
                    )
                    valid_records_to_save.append(drone_db_record)
                    pipeline_run.valid_records += 1
                except (ValidationError, ValueError, TypeError):
                    # [3] Remove or skip invalid records
                    pipeline_run.invalid_records += 1
                    continue
             #[5] Store valid records in the database (Bulk efficient saving)
            if valid_records_to_save:
               db.add_all(valid_records_to_save)
            # [6] Save pipeline run status and processing counters (Finalization)
            pipeline_run.status = "completed"
            pipeline_run.finished_at = datetime.now(timezone.utc)
            db.commit()

        
            return {"status": "success", "total_records": pipeline_run.total_records ,"valid_records": pipeline_run.valid_records, "Invalid_records" : pipeline_run.invalid_records}
        
    
        except Exception as e:
            # Handling general pipeline failures and rolling back unsafe data transitions
            db.rollback()
            pipeline_run.status = "failed"
            pipeline_run.finished_at = datetime.now(timezone.utc)
            pipeline_run.error_message = str(e)
            db.commit()
            return { "status" : "failed", "error": str(e)}