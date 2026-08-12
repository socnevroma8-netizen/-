# backend/models/db.py
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# База рядом с backend/
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "school.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},  # чтобы работало из разных потоков
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()