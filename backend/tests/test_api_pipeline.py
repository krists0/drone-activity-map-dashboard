import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.models.drone import DroneRecord


# Initialize the official FastAPI test orchestration client layer
client = TestClient(app)
def make_valid_drone():
    return DroneRecord(
        drone_id="DRONE-EDGE", 
        drone_type="VTOL", 
        operator_id="OP-999",
        latitude=32.0853,        
        longitude=34.7818,       
        altitude_m=120.0,  
        speed_kmh=45.0,         
        battery_percent=76,      
        timestamp=datetime.datetime.fromisoformat("2026-06-28T10:30:00"), 
        status="active"
    )



# CORE API LOGIC & PIPELINE INTEGRATION TESTS [3.1, 3.4]

def test_pipeline_trigger_ingestion_execution(db_session):
    """ Verifies execution logs report monitoring metrics dictionaries [3.2]. """
    db_session.add(make_valid_drone())
    db_session.commit()
    response = client.post("/api/pipeline/run")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "total_records" in data
    assert "valid_records" in data
    assert "invalid_records" in data  

def test_database_idempotency_deduplication_rule(db_session):
    """Verifies re-running files logs 0 modifications to guard storage [3.1]. """
    db_session.add(make_valid_drone())
    db_session.commit()
    first_run = client.post("/api/pipeline/run").json()
    second_run = client.post("/api/pipeline/run").json()
    assert second_run["valid_records"] == 0


# /api/pipeline/runs COVERAGE [3.4]

def test_get_pipeline_runs_returns_history_ordered_by_most_recent():
    client.post("/api/pipeline/run")
    client.post("/api/pipeline/run")

    response = client.get("/api/pipeline/runs")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 2
    assert runs[0]["id"] > runs[1]["id"]