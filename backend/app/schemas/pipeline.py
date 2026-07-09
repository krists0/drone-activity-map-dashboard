from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict, field_validator


PipelineStatus = Literal["started", "completed", "failed"]


class PiplineRunRead(BaseModel):
    id : int
    started_at : datetime
    finished_at : datetime | None
    status : PipelineStatus
    total_records : int
    valid_records : int
    invalid_records : int
    error_message : str | None

    model_config = ConfigDict(from_attributes=True)
    
class PiplineRunResult(BaseModel):
    run : PiplineRunRead