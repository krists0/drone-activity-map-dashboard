
import datetime
from fastapi.testclient import TestClient
from app.main import app
import json
from app.models.drone import DroneRecord
from app.services.pipeline_service import PipelineService

# Initialize the official FastAPI test orchestration client layer
client = TestClient(app)

# CORE PIPELINE LOGIC — DIRECT SERVICE TESTS (bypassing the fixed input file) [3.1]

def test_pipeline_service_skips_invalid_records_and_counts_correctly(tmp_path , db_session):
    """ The heart of the assignment: mixed valid/invalid input must be counted correctly [3.1, 3.3]. """
    input_file = tmp_path / "mixed_records.json"
    input_file.write_text(json.dumps([
        {  # valid
            "drone_id": "OK-1-TEST", "drone_type": "Quadcopter", "operator_id": "OP-1",
            "latitude": 32.0, "longitude": 34.0, "altitude_m": 100, "speed_kmh": 10,
            "battery_percent": 50, "timestamp": "2026-06-28T10:30:00Z", "status": "active"
        },
        {  # invalid: empty drone_id
            "drone_id": "", "drone_type": "Quadcopter", "operator_id": "OP-1",
            "latitude": 32.0, "longitude": 34.0, "altitude_m": 100, "speed_kmh": 10,
            "battery_percent": 50, "timestamp": "2026-06-28T10:30:00Z", "status": "active"
        },
        {  # invalid: bad status
            "drone_id": "BAD-1-TEST", "drone_type": "Quadcopter", "operator_id": "OP-1",
            "latitude": 32.0, "longitude": 34.0, "altitude_m": 100, "speed_kmh": 10,
            "battery_percent": 50, "timestamp": "2026-06-28T10:30:00Z", "status": "flying"
        },
    ]))

    result = PipelineService.run_ingestion_pipeline(db_session, str(input_file))
    assert result["status"] == "success"
    assert result["total_records"] == 3
    assert result["valid_records"] == 1
    assert result["invalid_records"] == 2
   

def test_pipeline_service_handles_missing_file_gracefully(db_session):
    """ Verifies pipeline_run.status becomes 'failed' with an error_message, not a crash [3.2]. """
   
    result = PipelineService.run_ingestion_pipeline(db_session, "/nonexistent/path.json")
    assert result["status"] == "failed"
    assert "error" in result
    


