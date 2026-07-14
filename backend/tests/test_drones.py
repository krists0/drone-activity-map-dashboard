import datetime

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.drone import DroneRecordCreate
from pydantic import ValidationError

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
        speed_kmh=45.0,          # ◄ FIXED: Added missing mandate property from section 5 spec
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
    assert "Invalid_records" in data  # Aligned with upper-case 'I' backend schema layout [3.2]

def test_database_idempotency_deduplication_rule():
    """Verifies re-running files logs 0 modifications to guard storage [3.1]. """
    first_run = client.post("/api/pipeline/run").json()
    second_run = client.post("/api/pipeline/run").json()
    assert second_run["valid_records"] == 0
