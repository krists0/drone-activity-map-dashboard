


from sqlalchemy import Column ,Integer ,Float ,String ,DateTime ,Text

from app.db.database import Base


class PipelineRun(Base):
    __tablename__= "pipline_runs"

    id = Column(Integer , primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, index=True)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    invalid_records = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
