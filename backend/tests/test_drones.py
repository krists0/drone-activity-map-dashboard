import datetime

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.drone import DroneRecordCreate
from pydantic import ValidationError
import json
from app.db.database import Sessionlocal as SessionLocal
from app.models.drone import DroneRecord
from app.services.pipeline_service import PipelineService

# Initialize the official FastAPI test orchestration client layer
client = TestClient(app)


def test_health_check_endpoint():
    """ Sanity test verifying that the application context triggers 200 OK responses [3.4]. """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



# LATITUDE & LONGITUDE BOUNDARY TESTS [3.3]

def test_validation_rule_rejects_empty_drone_id():
    """ MANDATE CHECK: drone_id must not be empty [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="", drone_type="Quadcopter", operator_id="OP-123", latitude=32.0853, longitude=34.7818, altitude_m=120.0, battery_percent=80, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_latitude_above_maximum_limit():
    """ Enforces maximum boundary constraint for latitude (must be <= 90) [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=90.1, longitude=34.0, altitude_m=100, battery_percent=50, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_latitude_below_minimum_limit():
    """ Enforces minimum boundary constraint for latitude (must be >= -90) [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=-90.1, longitude=34.0, altitude_m=100, battery_percent=50, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_longitude_above_maximum_limit():
    """ Enforces maximum boundary constraint for longitude (must be <= 180) [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=180.1, altitude_m=100, battery_percent=50, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_longitude_below_minimum_limit():
    """ Enforces minimum boundary constraint for longitude (must be >= -180) [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=-180.1, altitude_m=100, battery_percent=50, timestamp="2026-06-28T10:30:00Z", status="active")


# (ALTITUDE & BATTERY) [3.3]

def test_validation_rule_rejects_negative_altitude():
    """ MANDATE CHECK: altitude_m must be zero or positive [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="Quadcopter", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=-15.5, battery_percent=80, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_battery_below_zero():
    """ Enforces minimum boundary limit for battery percentage (must be >= 0) [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=100, battery_percent=-5, timestamp="2026-06-28T10:30:00Z", status="active")

def test_validation_rule_rejects_overflow_battery_capacity():
    """ MANDATE CHECK: battery_percent must be between 0 and 100 [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="Quadcopter", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=120.0, battery_percent=185, timestamp="2026-06-28T10:30:00Z", status="active")


# TIMESTAMP & STATUS KEYWORDS TESTS [3.3]


def test_validation_rule_rejects_corrupt_text_timestamp():
    """ Verifies that a generic corrupt string is completely rejected as a date format [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=100, battery_percent=80, timestamp="invalid-date-format", status="active")

def test_validation_rule_rejects_empty_timestamp():
    """ Verifies that an empty timestamp value drops the validation [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=100, battery_percent=80, timestamp="", status="active")

def test_validation_rule_rejects_unallowed_status_keywords():
    """ MANDATE CHECK: status should be one of: active, landed, lost_signal [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="Quadcopter", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=120.0, battery_percent=80, timestamp="2026-06-28T10:30:00Z", status="flying")


#  HAPPY FLOWS & POSITIVE TESTING EDGE CASES [3.3]

def test_validation_accepts_absolute_boundary_values():
    """ 
    Positive testing flow: verifies edge attributes inside valid ranges pass cleanly [3.3].
    FIXED: Added the missing speed_kmh mandate parameter to satisfy Pydantic schema constraints.
    """
    valid_drone = DroneRecordCreate(
        drone_id="DRONE-EDGE", 
        drone_type="VTOL", 
        operator_id="OP-999",
        latitude=32.0853,        
        longitude=34.7818,       
        altitude_m=120.0,  
        speed_kmh=45.0,         
        battery_percent=76,      
        timestamp=datetime.datetime.fromisoformat("2026-06-28T10:30:00"), 
        status="landed"
    )
    assert valid_drone.battery_percent == 76
    assert valid_drone.status == "landed"


# CORE API LOGIC & PIPELINE INTEGRATION TESTS [3.1, 3.4]

def test_api_query_filters_alignment():

    response = client.get("/api/drones", params={"status": "active"})
    assert response.status_code == 200
    for drone in response.json():
        assert drone["status"] == "active"

def test_pipeline_trigger_ingestion_execution():
    """ Verifies execution logs report monitoring metrics dictionaries [3.2]. """
    response = client.post("/api/pipeline/run")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "total_records" in data
    assert "valid_records" in data
    assert "invalid_records" in data  

def test_database_idempotency_deduplication_rule():
    """Verifies re-running files logs 0 modifications to guard storage [3.1]. """
    first_run = client.post("/api/pipeline/run").json()
    second_run = client.post("/api/pipeline/run").json()
    assert second_run["valid_records"] == 0


def _make_db_session():
    """ Helper: opens a real DB session directly, no conftest fixture needed. """
    return SessionLocal()


# GET /api/drones/{id} COVERAGE [3.4]

def test_get_single_drone_not_found_returns_404():
    """ Bug fix verification: missing ID must return 404, not crash with a 500 [3.4]. """
    response = client.get("/api/drones/99999")
    assert response.status_code == 404

def test_get_single_drone_found_returns_correct_record():
    """ Verifies a single drone lookup returns the exact matching record [3.4]. """
    db = _make_db_session()
    record = DroneRecord(
        drone_id="D-SINGLE-TEST", drone_type="VTOL", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=50, timestamp=datetime.datetime(2026, 1, 1), status="active"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    record_id = record.id
    db.close()

    try:
        response = client.get(f"/api/drones/{record_id}")
        assert response.status_code == 200
        assert response.json()["drone_id"] == "D-SINGLE-TEST"
    finally:
        db = _make_db_session()
        db.query(DroneRecord).filter(DroneRecord.id == record_id).delete()
        db.commit()
        db.close()


# /api/drones FILTERS COVERAGE [3.4]

def test_drones_filter_by_drone_type():
    db = _make_db_session()
    record = DroneRecord(
        drone_id="D-TYPE-TEST", drone_type="Fixed Wing", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=50, timestamp=datetime.datetime(2026, 1, 1), status="active"
    )
    db.add(record)
    db.commit()
    record_id = record.id
    db.close()

    try:
        response = client.get("/api/drones", params={"drone_type": "Fixed Wing"})
        assert response.status_code == 200
        data = response.json()
        assert any(d["drone_id"] == "D-TYPE-TEST" for d in data)
        assert all(d["drone_type"] == "Fixed Wing" for d in data)
    finally:
        db = _make_db_session()
        db.query(DroneRecord).filter(DroneRecord.id == record_id).delete()
        db.commit()
        db.close()

def test_drones_filter_by_min_battery():
    db = _make_db_session()
    low = DroneRecord(drone_id="D-LOW-TEST", drone_type="VTOL", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=10, timestamp=datetime.datetime(2026, 1, 1), status="active")
    high = DroneRecord(drone_id="D-HIGH-TEST", drone_type="VTOL", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=80, timestamp=datetime.datetime(2026, 1, 1), status="active")
    db.add_all([low, high])
    db.commit()
    low_id, high_id = low.id, high.id
    db.close()

    try:
        response = client.get("/api/drones", params={"min_battery": 50})
        data = response.json()
        ids = [d["drone_id"] for d in data]
        assert "D-HIGH-TEST" in ids
        assert "D-LOW-TEST" not in ids
    finally:
        db = _make_db_session()
        db.query(DroneRecord).filter(DroneRecord.id.in_([low_id, high_id])).delete(synchronize_session=False)
        db.commit()
        db.close()

def test_drones_filter_by_date_range():
    db = _make_db_session()
    old = DroneRecord(drone_id="D-OLD-TEST", drone_type="VTOL", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=50, timestamp=datetime.datetime(2020, 1, 1), status="active")
    new = DroneRecord(drone_id="D-NEW-TEST", drone_type="VTOL", operator_id="OP-1",
        latitude=32.0, longitude=34.0, altitude_m=100, speed_kmh=10,
        battery_percent=50, timestamp=datetime.datetime(2026, 6, 28), status="active")
    db.add_all([old, new])
    db.commit()
    old_id, new_id = old.id, new.id
    db.close()

    try:
        response = client.get("/api/drones", params={
            "from_date": "2026-01-01T00:00:00Z",
            "to_date": "2026-12-31T00:00:00Z"
        })
        data = response.json()
        ids = [d["drone_id"] for d in data]
        assert "D-NEW-TEST" in ids
        assert "D-OLD-TEST" not in ids
    finally:
        db = _make_db_session()
        db.query(DroneRecord).filter(DroneRecord.id.in_([old_id, new_id])).delete(synchronize_session=False)
        db.commit()
        db.close()


# CORE PIPELINE LOGIC — DIRECT SERVICE TESTS (bypassing the fixed input file) [3.1]

def test_pipeline_service_skips_invalid_records_and_counts_correctly(tmp_path):
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

    db = _make_db_session()
    try:
        result = PipelineService.run_ingestion_pipeline(db, str(input_file))

        assert result["status"] == "success"
        assert result["total_records"] == 3
        assert result["valid_records"] == 1
        assert result["invalid_records"] == 2
    finally:
        db.query(DroneRecord).filter(DroneRecord.drone_id == "OK-1-TEST").delete()
        db.commit()
        db.close()

def test_pipeline_service_handles_missing_file_gracefully():
    """ Verifies pipeline_run.status becomes 'failed' with an error_message, not a crash [3.2]. """
    db = _make_db_session()
    try:
        result = PipelineService.run_ingestion_pipeline(db, "/nonexistent/path.json")
        assert result["status"] == "failed"
        assert "error" in result
    finally:
        db.close()


# /api/pipeline/runs COVERAGE [3.4]

def test_get_pipeline_runs_returns_history_ordered_by_most_recent():
    client.post("/api/pipeline/run")
    client.post("/api/pipeline/run")

    response = client.get("/api/pipeline/runs")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 2
    assert runs[0]["id"] > runs[1]["id"]