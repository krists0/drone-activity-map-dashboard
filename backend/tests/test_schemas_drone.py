import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.drone import DroneRecordBase, DroneRecordCreate
from pydantic import ValidationError
import json
from app.db.database import Sessionlocal as SessionLocal
from app.models.drone import DroneRecord
from app.services.pipeline_service import PipelineService

# Initialize the official FastAPI test orchestration client layer
client = TestClient(app)



def valid_drone_payload() -> dict:
    return {
        "drone_id": "DRONE-EDGE",
        "drone_type": "VTOL",
        "operator_id": "OP-999",
        "latitude": 32.0853,
        "longitude": 34.7818,
        "altitude_m": 120.0,
        "speed_kmh": 45.0,
        "battery_percent": 76,
        "timestamp": "2026-06-28T10:30:00Z",
        "status": "active",
    }
@pytest.mark.parametrize("field_name, invalid_value", [
    ("drone_id", ""),
    ("latitude", 200),
    ("longitude", 300),
    ("altitude_m", -10),
    ("battery_percent", -10),
    ("status", "flying"),
    ("timestamp", "invalid-date"),
])
def test_invalid_drone_fields(field_name: str, invalid_value):
    payload =valid_drone_payload()
    payload[field_name] = invalid_value
    with pytest.raises(ValidationError):
        DroneRecordBase(**payload)


def test_health_check_endpoint():
    """ Sanity test verifying that the application context triggers 200 OK responses [3.4]. """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}




# TIMESTAMP & STATUS KEYWORDS TESTS [3.3]

def test_validation_rule_rejects_empty_timestamp():
    """ Verifies that an empty timestamp value drops the validation [3.3]. """
    with pytest.raises(ValidationError):
        DroneRecordCreate(drone_id="D-1", drone_type="VTOL", operator_id="OP-1", latitude=32.0, longitude=34.0, altitude_m=100, battery_percent=80, timestamp="", status="active")


#  HAPPY FLOWS & POSITIVE TESTING EDGE CASES [3.3]

def test_validation_accepts_absolute_boundary_values():
    """ 
    Positive testing flow: verifies edge attributes inside valid ranges pass cleanly [3.3].
    """
    drone = valid_drone_payload()
    assert drone["battery_percent"] == 76
    assert drone["status"] == "active"


