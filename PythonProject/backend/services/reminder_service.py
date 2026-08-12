import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "app.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_reminders():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, text, date, time FROM reminders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    return [
        {"id": r[0], "text": r[1], "date": r[2], "time": r[3]}
        for r in rows
    ]


def add_reminder(text, date, time):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (text, date, time) VALUES (?, ?, ?)",
        (text, date, time),
    )
    conn.commit()
    conn.close()