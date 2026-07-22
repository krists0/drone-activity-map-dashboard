import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Sessionlocal as SessionLocal
from app.models.drone import DroneRecord


# Initialize the official FastAPI test orchestration client layer
client = TestClient(app)
def make_valid_drone(**overrides) -> DroneRecord:
    defaults = {
        "drone_id": "D-DEFAULT",
        "drone_type": "VTOL",
        "operator_id": "OP-1",
        "latitude": 32.0,
        "longitude": 34.0,
        "altitude_m": 100,
        "speed_kmh": 10,
        "battery_percent": 50,
        "timestamp": datetime.datetime(2026, 1, 1),
        "status": "active",
    }
    defaults.update(overrides)
    return DroneRecord(**defaults)

def test_api_query_filters_alignment(db_session):
    db_session.add(make_valid_drone(status="active"))
    db_session.commit()
    response = client.get("/api/drones", params={"status": "active"})
    assert response.status_code == 200
    for drone in response.json():
        assert drone["status"] == "active"

# GET /api/drones/{id} COVERAGE [3.4]

def test_get_single_drone_not_found_returns_404():
    """ Bug fix verification: missing ID must return 404, not crash with a 500 [3.4]. """
    response = client.get("/api/drones/99999")
    assert response.status_code == 404

def test_get_single_drone_found_returns_correct_record(db_session):
    """ Verifies a single drone lookup returns the exact matching record [3.4]. """
    
    record = make_valid_drone(drone_id="D-SINGLE-TEST")
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    response = client.get(f"/api/drones/{record.id}")
    assert response.status_code == 200
    assert response.json()["drone_id"] == "D-SINGLE-TEST"
    
# /api/drones FILTERS COVERAGE [3.4]
def test_drones_filter_by_drone_type(db_session):

    record = make_valid_drone(drone_id="D-TYPE-TEST", drone_type="Fixed Wing")

    db_session.add(record)
    db_session.commit()

    response = client.get("/api/drones", params={"drone_type": record.drone_type})
    assert response.status_code == 200
    data = response.json()
    assert any(d["drone_id"] == "D-TYPE-TEST" for d in data)
    assert all(d["drone_type"] == "Fixed Wing" for d in data)
    
def test_drones_filter_by_min_battery(db_session):

    db_session.add_all([ make_valid_drone(drone_id="D-LOW-TEST", battery_percent=10),
        make_valid_drone(drone_id="D-HIGH-TEST", battery_percent=80),])
    db_session.commit()
    
    response = client.get("/api/drones", params={"min_battery": 50})
    data = response.json()
    ids = [d["drone_id"] for d in data]
    assert "D-HIGH-TEST" in ids
    assert "D-LOW-TEST" not in ids
   
def test_drones_filter_by_date_range(db_session):
    db_session.add_all([make_valid_drone(drone_id="D-OLD-TEST", timestamp=datetime.datetime(2020, 1, 1)), make_valid_drone(drone_id="D-NEW-TEST", timestamp=datetime.datetime(2026, 6, 28))])
    db_session.commit()
    response = client.get("/api/drones", params={
            "from_date": "2026-01-01T00:00:00Z",
            "to_date": "2026-12-31T00:00:00Z"
    })
    data = response.json()
    ids = [d["drone_id"] for d in data]
    assert "D-NEW-TEST" in ids
    assert "D-OLD-TEST" not in ids
   
