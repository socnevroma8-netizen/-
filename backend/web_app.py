from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Form, Depends, Query
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


def class_key_for(user):
    class_key = user["grade"]
    if user.get("profile"):
        class_key = f'{user["grade"]} / {user["profile"]}'
    return class_key


def redirect_if_anonymous(request: Request, db):
    user = current_user(request, db)
    if not user:
        return None, RedirectResponse(url="/web/login", status_code=302)
    return user, None


def lessons_for_class(db, class_key):
    return db.execute(
        text(
            "SELECT day, lesson_number, lesson_time, subject, teacher_name, cabinet "
            "FROM lessons WHERE grade = :grade ORDER BY lesson_number"
        ),
        {"grade": class_key},
    ).mappings().all()


def teacher_directory(db, search=None):
    rows = db.execute(
        text("SELECT teacher_name, subject, cabinet FROM lessons WHERE teacher_name IS NOT NULL AND teacher_name <> '' ORDER BY teacher_name, subject")
    ).mappings().all()
    teachers = {}
    query = (search or "").strip().lower()
    for row in rows:
        name = row["teacher_name"]
        subject = row["subject"] or ""
        if query and query not in f"{name} {subject}".lower():
            continue
        item = teachers.setdefault(name, {"name": name, "subjects": set(), "cabinets": set()})
        if subject:
            item["subjects"].add(subject)
        if row["cabinet"]:
            item["cabinets"].add(str(row["cabinet"]))
    return [
        {"name": item["name"], "subjects": sorted(item["subjects"]), "cabinets": sorted(item["cabinets"])}
        for item in sorted(teachers.values(), key=lambda value: value["name"].lower())
    ]


@router.get("/", response_class=HTMLResponse)
def web_root(request: Request, db=Depends(get_db)):
    user = current_user(request, db)
    if user:
        return RedirectResponse(url="/web/home", status_code=302)
    return RedirectResponse(url="/web/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="web_login.html", context={"error": None})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...), db=Depends(get_db)):
    row = db.execute(
        text("SELECT id, full_name, username, password, role, is_admin, grade, profile FROM users WHERE username = :username"),
        {"username": username},
    ).mappings().first()
    if not row or row["password"] != password:
        return templates.TemplateResponse(request=request, name="web_login.html", context={"error": "Неверный логин или пароль"}, status_code=401)
    request.session["user_id"] = row["id"]
    request.session["username"] = row["username"]
    request.session["full_name"] = row["full_name"]
    request.session["is_admin"] = row["is_admin"]
    return RedirectResponse(url="/web/home", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/web/login", status_code=302)


@router.get("/home", response_class=HTMLResponse)
def home_page(request: Request, db=Depends(get_db)):
    user, redirect = redirect_if_anonymous(request, db)
    if redirect:
        return redirect
    today = datetime.now()
    day_name = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][today.weekday()]
    lessons = [dict(row) for row in lessons_for_class(db, class_key_for(user)) if row["day"] == day_name]
    return templates.TemplateResponse(request=request, name="web_home.html", context={"user": user, "lessons": lessons, "today_label": today.strftime("%d.%m.%Y")})


@router.get("/schedule", response_class=HTMLResponse)
def schedule_page(request: Request, db=Depends(get_db)):
    user, redirect = redirect_if_anonymous(request, db)
    if redirect:
        return redirect
    rows = lessons_for_class(db, class_key_for(user))
    days = {}
    for row in rows:
        days.setdefault(row["day"], []).append(dict(row))
    ordered_days = [(day, days[day]) for day in DAY_ORDER if day in days]
    return templates.TemplateResponse(request=request, name="web_schedule.html", context={"user": user, "days": ordered_days, "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M")})


@router.get("/teachers", response_class=HTMLResponse)
def teachers_page(request: Request, search: str = Query(default=""), db=Depends(get_db)):
    user, redirect = redirect_if_anonymous(request, db)
    if redirect:
        return redirect
    return templates.TemplateResponse(request=request, name="web_section.html", context={"user": user, "title": "Преподаватели", "message": "", "teachers": teacher_directory(db, search), "search": search})


@router.get("/{section}", response_class=HTMLResponse)
def section_page(section: str, request: Request, db=Depends(get_db)):
    user, redirect = redirect_if_anonymous(request, db)
    if redirect:
        return redirect
    sections = {
        "users": ("База пользователей", "Раздел пользователей будет доступен администраторам."),
        "reminders": ("Напоминания", "Здесь будут отображаться напоминания."),
        "transfers": ("Трансферы", "Здесь будут отображаться замены и переносы."),
    }
    if section not in sections:
        return HTMLResponse("Раздел не найден", status_code=404)
    title, message = sections[section]
    if section == "users" and not user.get("is_admin"):
        return HTMLResponse("Доступ разрешён только администраторам", status_code=403)
    return templates.TemplateResponse(request=request, name="web_section.html", context={"user": user, "title": title, "message": message})
