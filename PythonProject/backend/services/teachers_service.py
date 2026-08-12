import pandas as pd
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
USERS_XLSX = PROJECT_DIR / "mobile" / "data" / "users.xlsx"

def get_teachers():
    df = pd.read_excel(USERS_XLSX, sheet_name="Педагоги")
    result = []

    for _, row in df.iterrows():
        result.append({
            "fio": str(row["ФИО"]).strip(),
            "subject": str(row["Предмет"]).strip(),
            "room": str(row["Кабинет"]).strip(),
            "login": str(row["Логин"]).strip(),
            "is_admin": str(row["Админ"]).strip().lower() == "админ",
        })

    return result