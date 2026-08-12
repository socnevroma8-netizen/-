from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .schedule_service import ScheduleService
from .user_service import UserService
from .teachers_service import get_teachers

router = APIRouter(prefix="/api", tags=["api"])

user_service = UserService()
schedule_service = ScheduleService()



class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
def api_login(payload: LoginRequest):
    user_service.reload()

    user = user_service.login(
        payload.login,
        payload.password,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль",
        )

    return {
        "login": payload.login,
        "fio": user.get("fio", ""),
        "role": user.get("role", ""),
        "klass": user.get("klass", ""),
        "profile": user.get("profile", ""),
        "subject": user.get("teacher_subject", ""),
        "cabinet": user.get("teacher_cabinet", ""),
        "admin": bool(user.get("is_admin", False)),
        "classroom": user.get("teacher_classroom_teacher", ""),
    }


@router.get("/schedule/student")
def student_schedule(
    klass: str = Query(..., description="Класс, например 7Б"),
    profile: str = Query("", description="Профиль класса"),
    day: Optional[str] = Query(None, description="День недели"),
):
    items = schedule_service.get_student_schedule(
        klass=klass,
        profile=profile,
        day=day,
    )

    return {
        "klass": klass,
        "profile": profile,
        "day": day,
        "items": items,
    }


@router.get("/schedule/teacher")
def teacher_schedule(
    fio: str = Query(..., description="ФИО преподавателя"),
    day: Optional[str] = Query(None, description="День недели"),
):
    items = schedule_service.get_teacher_schedule(
        fio=fio,
        day=day,
    )

    return {
        "fio": fio,
        "day": day,
        "items": items,
    }


@router.get("/schedule/today/student")
def today_student_schedule(
    klass: str = Query(..., description="Класс, например 7Б"),
    profile: str = Query("", description="Профиль класса"),
):
    return schedule_service.get_today_for_student(
        klass=klass,
        profile=profile,
    )


@router.get("/schedule/today/teacher")
def today_teacher_schedule(
    fio: str = Query(..., description="ФИО преподавателя"),
):
    return schedule_service.get_today_for_teacher(fio=fio)

@router.get("/teachers")
def api_get_teachers():
    return {
        "items": get_teachers()
    }