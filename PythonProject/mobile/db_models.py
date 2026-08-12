# mobile/db_models.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mobile.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile: Mapped[str | None] = mapped_column(String(100), nullable=True)

    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(150), nullable=True)
    cabinet: Mapped[str | None] = mapped_column(String(50), nullable=True)
    homeroom: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[str] = mapped_column(String(50), nullable=False)
    profile: Mapped[str | None] = mapped_column(String(100), nullable=True)
    day: Mapped[str] = mapped_column(String(30), nullable=False)
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_time: Mapped[str | None] = mapped_column(String(30), nullable=True)
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    teacher_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cabinet: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    remind_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="reminders")