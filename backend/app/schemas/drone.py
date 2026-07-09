from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator



DroneStatus = Literal["active", "flying", "lost_signal"]


class DroneRecordBase(BaseModel):
     

    drone_id : str = Field(..., min_length=1)
    drone_type : str = Field(..., min_length=1)
    operator_id : str = Field(...,min_length=1)
    latitude : float = Field(..., ge=-90 , le=180)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float = Field(..., ge=0)
    speed_kmh: float = Field(..., ge=0)
    battery_percent: int = Field(..., ge=0, le=100)
    timestamp: datetime
    status: DroneStatus

    @field_validator("drone_id", "drone_type", "operator_id")
    @classmethod
    def must_not_be_blank(cls, value: str)-> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Field must not be empty")

        return cleaned_value
    
class DroneRecordCreate(DroneRecordBase):
    pass

class DroneRecordRead(DroneRecordBase):
    id: int

    model_config = ConfigDict(from_attributes=True)