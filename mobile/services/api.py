from datetime import datetime
from pathlib import Path

import requests


API_BASE_URL = "http://127.0.0.1:8000"


class ApiError(Exception):
    pass


def _handle_response(response, default_message: str):
    try:
        data = response.json()
    except Exception:
        data = {}

    print("API STATUS:", response.status_code)
    print("API URL:", response.url)
    print("API RESPONSE:", data)

    if response.status_code >= 400:
        detail = data.get("detail") if isinstance(data, dict) else None
        raise ApiError(
            f"{detail or default_message} (HTTP {response.status_code})"
        )

    return data


def normalize_profile(profile: str) -> str:
    value = (profile or "").strip()
    mapping = {
        "ИнфоТех": "Инфотех",
        "ФизМат": "Физмат",
        "ХимБио": "Химбио",
    }
    return mapping.get(value, value)


def normalize_role(role: str) -> str:
    value = (role or "").strip().lower()

    if value in {
        "student",
        "ученик",
        "ученица",
        "учащийся",
        "учащаяся",
    }:
        return "student"

    if value in {
        "teacher",
        "педагог",
        "учитель",
        "учительница",
        "преподаватель",
    }:
        return "teacher"

    return value


def current_weekday() -> str:
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]
    return weekdays[datetime.now().weekday()]


def login(login: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/login",
            json={"login": login, "password": password},
            timeout=10,
        )
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")

    return _handle_response(response, "Ошибка входа")


def get_today_schedule(
    role: str,
    klass: str = "",
    profile: str = "",
    fio: str = "",
):
    role_value = normalize_role(role)
    day = current_weekday()

    try:
        if role_value == "student":
            response = requests.get(
                f"{API_BASE_URL}/api/schedule/student",
                params={
                    "klass": klass,
                    "profile": normalize_profile(profile),
                    "day": day,
                },
                timeout=10,
            )
        elif role_value == "teacher":
            response = requests.get(
                f"{API_BASE_URL}/api/schedule/teacher",
                params={
                    "fio": fio,
                    "day": day,
                },
                timeout=10,
            )
        else:
            raise ApiError(f"Неизвестная роль пользователя: {role}")
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")

    return _handle_response(
        response,
        "Ошибка загрузки расписания на сегодня",
    )


def get_week_schedule(
    day: str,
    role: str,
    klass: str = "",
    profile: str = "",
    fio: str = "",
):
    role_value = normalize_role(role)

    try:
        if role_value == "student":
            response = requests.get(
                f"{API_BASE_URL}/api/schedule/student",
                params={
                    "klass": klass,
                    "profile": normalize_profile(profile),
                    "day": day,
                },
                timeout=10,
            )
        elif role_value == "teacher":
            response = requests.get(
                f"{API_BASE_URL}/api/schedule/teacher",
                params={
                    "fio": fio,
                    "day": day,
                },
                timeout=10,
            )
        else:
            raise ApiError(f"Неизвестная роль пользователя: {role}")
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")

    return _handle_response(response, "Ошибка загрузки расписания")


def create_user(
    fio: str,
    role: str,
    login: str,
    password: str,
    klass: str = "",
    profile: str = "",
    subject: str = "",
    cabinet: str = "",
    classroom: str = "",
    admin: bool = False,
):
    payload = {
        "fio": fio,
        "role": role,
        "login": login,
        "password": password,
        "klass": klass,
        "profile": profile,
        "subject": subject,
        "cabinet": cabinet,
        "classroom": classroom,
        "admin": admin,
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/admin/users",
            json=payload,
            timeout=10,
        )
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")

    return _handle_response(
        response,
        "Ошибка создания пользователя",
    )


def upload_schedule(file_path: str):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                f"{API_BASE_URL}/api/admin/schedule/upload",
                files={
                    "file": (
                        Path(file_path).name,
                        file,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
                timeout=20,
            )
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")
    except OSError as error:
        raise ApiError(f"Ошибка чтения файла: {error}")

    return _handle_response(response, "Ошибка загрузки расписания")


def get_today_student(klass: str, profile: str):
    return get_today_schedule(
        "student",
        klass=klass,
        profile=profile,
    )


def get_today_teacher(fio: str):
    return get_today_schedule("teacher", fio=fio)


def get_schedule_student(klass: str, profile: str, day: str):
    return get_week_schedule(
        day,
        "student",
        klass=klass,
        profile=profile,
    )


def get_schedule_teacher(fio: str, day: str):
    return get_week_schedule(
        day,
        "teacher",
        fio=fio,
    )
def get_teachers():
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/teachers",
            timeout=10,
        )
    except requests.RequestException as error:
        raise ApiError(f"Ошибка соединения: {error}")

    return _handle_response(
        response,
        "Ошибка загрузки списка учителей",
    )