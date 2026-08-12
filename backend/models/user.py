# backend/models/user.py
from sqlalchemy import Column, Integer, String
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)       # ФИО
    role = Column(String, nullable=False)            # 'admin' | 'teacher' | 'student'
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)        # для простоты — в открытом виде
    grade = Column(String, nullable=True)            # класс / группа
    subject = Column(String, nullable=True)          # предмет (для педагога)
    cabinet = Column(String, nullable=True)          # кабинет
    homeroom = Column(String, nullable=True)         # классное руководство (напр. "5А")