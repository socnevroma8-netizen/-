import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
USERS_XLSX = DATA_DIR / "users.xlsx"


def norm(value: str) -> str:
    return str(value).strip().lower()


def login_student(username: str, password: str):
    df = pd.read_excel(USERS_XLSX, sheet_name="Ученики")
    df["login_norm"] = df["Логин"].astype(str).str.strip().str.lower()
    df["password_norm"] = df["Пароль"].astype(str).str.strip().str.lower()

    row = df[
        (df["login_norm"] == norm(username)) &
        (df["password_norm"] == norm(password))
    ]

    if row.empty:
        return None

    user = row.iloc[0]
    return {
        "fio": str(user["ФИО"]).strip(),
        "klass": str(user["Класс"]).strip(),
        "profile": str(user["Профиль"]).strip(),
        "admin": str(user["Админ"]).strip().lower() == "админ",
    }