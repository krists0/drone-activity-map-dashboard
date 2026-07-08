

from fastapi import FastAPI
from datetime import datetime, timezone

from app.db.database import Base, engine
from app.models import PipelineRun , DroneRecord


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Drone Activity Map Dashboard API",
    version="0.1.0"
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}



@app.get("/")
def drone_print():
  
    mock_drone = DroneRecord(
        drone_id="DRONE-TEST-99",
        drone_type="Quadcopter",
        operator_id="OP-777",
        latitude=32.0853,
        longitude=34.7818,
        altitude_m=150.0,
        speed_kmh=50.0,
        battery_percent=88,
        timestamp = datetime.now(timezone.utc),
        status="active"
    )
    
   
    print("====================================")
    print(mock_drone)
    print("====================================")
    
    
    return {
        "message": "Drone printed in terminal successfully!",
        "drone_id": mock_drone.drone_id,
        "status": mock_drone.status,
        "battery": mock_drone.battery_percent,
        "test" : mock_drone.altitude_m
    }