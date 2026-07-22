import csv
import json
import os
from datetime import datetime, timezone

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.models.drone import DroneRecord
from app.models.pipeline import PipelineRun
from app.schemas.drone import DroneRecordBase


def load_json(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_records(file_path: str) -> list[dict]:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".json":
        return load_json(file_path)
    elif extension == ".csv":
        return load_csv(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")


def process_record(db: Session, record: dict) -> DroneRecord | None:
    """
    Validates a single raw record and checks for duplicates.
    Returns a DroneRecord ready to be saved, or None if invalid/duplicate.
    """
    try:
        validated_json = DroneRecordBase(**record)
    except (ValidationError, ValueError, TypeError):
        return None

    existing_record = (
        db.query(DroneRecord)
        .filter(
            DroneRecord.drone_id == validated_json.drone_id,
            DroneRecord.timestamp == validated_json.timestamp,
        )
        .first()
    )
    if existing_record:
        return None

    return DroneRecord(
        drone_id=validated_json.drone_id,
        drone_type=validated_json.drone_type,
        operator_id=validated_json.operator_id,
        latitude=validated_json.latitude,
        longitude=validated_json.longitude,
        altitude_m=validated_json.altitude_m,
        speed_kmh=validated_json.speed_kmh,
        battery_percent=validated_json.battery_percent,
        timestamp=validated_json.timestamp,
        status=validated_json.status,
    )

CHUNK_SIZE = 10

def save_in_chunks(db: Session, pipeline_run: PipelineRun, records: list[DroneRecord]) -> None: 
    for i in range(0, len(records), CHUNK_SIZE):
        chunk = records[i:i + CHUNK_SIZE]
        print(f"Chunk saved: {len(chunk)} records, total so far: {pipeline_run.valid_records}")
        db.add_all(chunk)
        db.commit()
        pipeline_run.valid_records += len(chunk) 
        db.commit()
        
class PipelineService:
    @staticmethod
    def run_ingestion_pipeline(db: Session, file_path: str) -> dict:
        pipeline_run = PipelineRun(status="started", started_at=datetime.now(timezone.utc))
        db.add(pipeline_run)
        db.commit()

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found at: {file_path}")

            raw_records = load_records(file_path)

            if not isinstance(raw_records, list):
                raise ValueError("Input file must contain a list of drone records")

            pipeline_run.total_records = len(raw_records)
            pipeline_run.valid_records = 0
            pipeline_run.invalid_records = 0
            db.commit()

            valid_records_to_save = []

            for record in raw_records:
                drone_db_record = process_record(db, record)
                if drone_db_record is not None:
                    valid_records_to_save.append(drone_db_record)
                else:
                    pipeline_run.invalid_records += 1

            # if valid_records_to_save:
            #     db.add_all(valid_records_to_save)
            if valid_records_to_save:
                save_in_chunks(db, pipeline_run, valid_records_to_save)
            pipeline_run.status = "completed"
            pipeline_run.finished_at = datetime.now(timezone.utc)
            db.commit()

            return {
                "status": "success",
                "total_records": pipeline_run.total_records,
                "valid_records": pipeline_run.valid_records,
                "invalid_records": pipeline_run.invalid_records,
            }

        except Exception as e:
            db.rollback()
            pipeline_run.status = "failed"
            pipeline_run.finished_at = datetime.now(timezone.utc)
            pipeline_run.error_message = str(e)
            db.commit()
            return {"status": "failed", "error": str(e)}