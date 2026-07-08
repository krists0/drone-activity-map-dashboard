from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings


engine = create_engine(settings.database_url)

Sessionlocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()