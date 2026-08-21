from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from .models.db import SessionLocal

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/web", tags=["web"])

DAY_ORDER = [
    "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_user(request: Request, db):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    row = db.execute(
        text("SELECT id, full_name, username, role, is_admin, grade, profile FROM users WHERE id = :id"),
        {"id": user_id},
    ).mappings().first()
    return dict(row) if row else None


@router.get("/", response_class=HTMLResponse)
def web_root(request: Request, db=Depends(get_db)):
    user = current_user(request, db)
    if user:
        return RedirectResponse(url="/web/schedule", status_code=302)
    return RedirectResponse(url="/web/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="web_login.html",
        context={"error": None},
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db),
):
    row = db.execute(
        text(
            "SELECT id, full_name, username, password, role, is_admin, grade, profile "
            "FROM users WHERE username = :username"
        ),
        {"username": username},
    ).mappings().first()

    if not row or row["password"] != password:
        return templates.TemplateResponse(
            request=request,
            name="web_login.html",
            context={"error": "Неверный логин или пароль"},
            status_code=401,
        )

    request.session["user_id"] = row["id"]
    request.session["username"] = row["username"]
    request.session["full_name"] = row["full_name"]
    request.session["is_admin"] = row["is_admin"]
    return RedirectResponse(url="/web/schedule", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/web/login", status_code=302)


@router.get("/schedule", response_class=HTMLResponse)
def schedule_page(request: Request, db=Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse(url="/web/login", status_code=302)

    rows = db.execute(
        text(
            "SELECT day, lesson_number, lesson_time, subject, teacher_name, cabinet "
            "FROM lessons WHERE grade = :grade "
            "ORDER BY lesson_number"
        ),
        {"grade": user["grade"]},
    ).mappings().all()

    days = {}
    for row in rows:
        days.setdefault(row["day"], []).append(dict(row))

    ordered_days = [(day, days[day]) for day in DAY_ORDER if day in days]
    for day in days:
        if day not in DAY_ORDER:
            ordered_days.append((day, days[day]))

    return templates.TemplateResponse(
        request=request,
        name="web_schedule.html",
        context={
            "user": user,
            "days": ordered_days,
            "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        },
    )
