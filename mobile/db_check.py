# mobile/db_check.py
from fastapi import FastAPI
from sqlalchemy import func, inspect, select, text

from mobile import db_models
from mobile.database import Base, SessionLocal, engine
from mobile.db_models import Lesson, Reminder, Teacher, User


Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Schedule API")


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "ok": True,
        "database": "postgresql",
    }


@app.get("/health/tables")
def database_tables():
    inspector = inspect(engine)

    return {
        "tables": inspector.get_table_names(),
    }


@app.get("/health/stats")
def database_stats():
    with SessionLocal() as db:
        users_count = db.scalar(
            select(func.count()).select_from(User)
        )
        teachers_count = db.scalar(
            select(func.count()).select_from(Teacher)
        )
        lessons_count = db.scalar(
            select(func.count()).select_from(Lesson)
        )
        reminders_count = db.scalar(
            select(func.count()).select_from(Reminder)
        )

    return {
        "users": users_count,
        "teachers": teachers_count,
        "lessons": lessons_count,
        "reminders": reminders_count,
    }