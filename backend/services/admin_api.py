# backend/services/admin_api.py
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from mobile.migrate_schedule import migrate_schedule
from pydantic import BaseModel

from .user_service import UserService  # тот, что выше
from .api import schedule_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

user_service = UserService()


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
SCHEDULE_XLSX = (
    PROJECT_ROOT
    / "mobile"
    / "data"
    / "schedule.xlsx"
)  # твой файл расписания [file:556]
migrate_schedule(SCHEDULE_XLSX)
schedule_service.reload()

class AdminUserCreate(BaseModel):
    fio: str
    role: str                 # "student" или "teacher"
    login: str
    password: str
    klass: str | None = None
    profile: str | None = None
    subject: str | None = None
    cabinet: str | None = None
    classroom: str | None = None
    admin: bool = False


@router.post("/users")
def admin_create_user(payload: AdminUserCreate):
    """
    Создание ученика или педагога в users.xlsx.
    """
    try:
        created = user_service.create_user(
            fio=payload.fio,
            role=payload.role,
            login=payload.login,
            password=payload.password,
            klass=payload.klass or "",
            profile=payload.profile or "",
            subject=payload.subject or "",
            cabinet=payload.cabinet or "",
            classroom=payload.classroom or "",
            admin=payload.admin,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "login": payload.login,
        "fio": created["fio"],
        "role": created["role"],
        "klass": created["klass"],
        "profile": created["profile"],
        "subject": created["teacher_subject"],
        "cabinet": created["teacher_cabinet"],
        "admin": created["is_admin"],
        "classroom": created["teacher_classroom_teacher"],
    }


@router.post("/schedule/upload")
async def admin_schedule_upload(file: UploadFile = File(...)):
    filename = file.filename or ""

    if not filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Нужен файл .xlsx",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Файл пустой",
        )

    try:
        SCHEDULE_XLSX.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        SCHEDULE_XLSX.write_bytes(content)

        lessons_count = migrate_schedule(SCHEDULE_XLSX)
        schedule_service.reload()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обновления расписания: {error}",
        )

    return {
        "ok": True,
        "filename": filename,
        "saved_as": SCHEDULE_XLSX.name,
        "lessons_count": lessons_count,
    }