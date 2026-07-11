


from sqlalchemy import Column ,Integer ,Float ,String ,DateTime

from app.db.database import Base


class DroneRecord(Base):
    __tablename__= "drone_records"

    id = Column(Integer , primary_key=True, index=True)
    drone_id = Column(String , index=True , nullable=False)
    drone_type = Column(String , index=True , nullable=False)
    operator_id = Column(String , index=True , nullable=False)
    latitude = Column(Float, index=True , nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    altitude_m = Column(Float, index=True, nullable=False)
    speed_kmh = Column(Float, index=True, nullable=False)
    battery_percent = Column(Integer, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String, index=True , nullable=False)


    def __repr__(self) -> str:
        return f"<DroneRecord(drone_id='{self.drone_id}', status='{self.status}', battery={self.battery_percent}%)>"
