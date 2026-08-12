from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import select

from mobile.database import SessionLocal
from mobile.db_models import Lesson


DAY_NAMES = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

DAY_ALIASES = {
    "пн": "понедельник",
    "понедельник": "понедельник",
    "вт": "вторник",
    "вторник": "вторник",
    "ср": "среда",
    "среда": "среда",
    "чт": "четверг",
    "четверг": "четверг",
    "пт": "пятница",
    "пятница": "пятница",
    "сб": "суббота",
    "суббота": "суббота",
    "вс": "воскресенье",
    "воскресенье": "воскресенье",
}

PROFILE_ALIASES = {
    "инфотех": "инфотех",
    "инфо тех": "инфотех",
    "инфо-тех": "инфотех",
    "физмат": "физмат",
    "физ мат": "физмат",
    "физ-мат": "физмат",
    "химбио": "химбио",
    "хим био": "химбио",
    "хим-био": "химбио",
}


class ScheduleService:
    def __init__(self) -> None:
        self.rows: List[Dict] = []
        self.class_map: Dict[str, dict] = {}
        self._load_schedule()

    @staticmethod
    def _normalize(value: Optional[str]) -> str:
        value = str(value or "").strip().lower().replace("ё", "е")
        return " ".join(
            value.replace("/", " ").replace("-", " ").split()
        )

    @classmethod
    def _normalize_day(cls, value: Optional[str]) -> str:
        normalized = cls._normalize(value)
        return DAY_ALIASES.get(normalized, normalized)

    @classmethod
    def _normalize_profile(cls, value: Optional[str]) -> str:
        normalized = cls._normalize(value)
        return PROFILE_ALIASES.get(normalized, normalized)

    @classmethod
    def _normalize_class(cls, value: Optional[str]) -> str:
        return cls._normalize(value).replace(" ", "")

    @staticmethod
    def _lesson_to_row(lesson: Lesson) -> Dict:
        lesson_number = getattr(lesson, "lesson_number", None)

        return {
            "day": str(getattr(lesson, "day", "") or "").strip(),
            "lesson": str(lesson_number or "").strip(),
            "lesson_sort": int(lesson_number or 0),
            "time": str(
                getattr(lesson, "lesson_time", "") or ""
            ).strip(),
            "class_name": str(
                getattr(lesson, "grade", "") or ""
            ).strip(),
            "subject": str(
                getattr(lesson, "subject", "") or ""
            ).strip(),
            "cabinet": str(
                getattr(lesson, "cabinet", "") or ""
            ).strip(),
            "teacher": str(
                getattr(lesson, "teacher_name", "") or ""
            ).strip(),
        }

    def _load_schedule(self) -> None:
        self.rows = []
        self.class_map = {}

        with SessionLocal() as db:
            lessons = db.execute(
                select(Lesson).order_by(
                    Lesson.grade,
                    Lesson.day,
                    Lesson.lesson_number,
                )
            ).scalars().all()

        for lesson in lessons:
            row = self._lesson_to_row(lesson)

            if not row["class_name"]:
                continue

            self.rows.append(row)

            if row["class_name"] not in self.class_map:
                self.class_map[row["class_name"]] = {}

        print(
            "[schedule_service] loaded from PostgreSQL: "
            f"{len(self.rows)} rows"
        )
        print(
            "[schedule_service] classes: "
            f"{list(self.class_map)[:15]}"
        )

    def _find_student_class_key(
        self,
        klass: str,
        profile: Optional[str],
    ) -> Optional[str]:
        requested_class = self._normalize_class(klass)
        requested_profile = self._normalize_profile(profile)

        candidates = []

        if requested_profile:
            candidates.extend(
                [
                    f"{requested_class}{requested_profile}",
                    f"{requested_class} {requested_profile}",
                ]
            )

        candidates.append(requested_class)

        normalized_map = {
            self._normalize_class(class_name): class_name
            for class_name in self.class_map
        }

        for candidate in candidates:
            candidate_normalized = self._normalize_class(candidate)

            if candidate_normalized in normalized_map:
                return normalized_map[candidate_normalized]

        for normalized_name, original_name in normalized_map.items():
            if not normalized_name.startswith(requested_class):
                continue

            if (
                not requested_profile
                or requested_profile in normalized_name
            ):
                return original_name

        return None

    def _filter_day(
        self,
        rows: List[Dict],
        day: Optional[str],
    ) -> List[Dict]:
        if not day:
            return rows

        requested_day = self._normalize_day(day)

        return [
            row
            for row in rows
            if self._normalize_day(row.get("day")) == requested_day
        ]

    @staticmethod
    def _public_row(row: Dict) -> Dict:
        return {
            "day": row["day"],
            "num": row["lesson"],
            "number": row["lesson"],
            "name": row["subject"],
            "subject": row["subject"],
            "time": row["time"],
            "room": row["cabinet"],
            "cabinet": row["cabinet"],
            "teacher": row["teacher"],
        }

    def get_student_schedule(
        self,
        klass: str,
        profile: Optional[str],
        day: Optional[str] = None,
    ) -> List[Dict]:
        class_key = self._find_student_class_key(klass, profile)

        if not class_key:
            print(
                "[schedule_service] class not found: "
                f"klass={klass!r}, profile={profile!r}"
            )
            return []

        rows = [
            row
            for row in self.rows
            if row["class_name"] == class_key
        ]

        rows = self._filter_day(rows, day)
        rows.sort(key=lambda row: row["lesson_sort"])

        return [self._public_row(row) for row in rows]

    def get_teacher_schedule(
        self,
        fio: str,
        day: Optional[str] = None,
    ) -> List[Dict]:
        requested_teacher = self._normalize(fio)

        rows = [
            row
            for row in self.rows
            if requested_teacher
            and requested_teacher in self._normalize(row["teacher"])
        ]

        rows = self._filter_day(rows, day)
        rows.sort(
            key=lambda row: (
                row["day"],
                row["lesson_sort"],
            )
        )

        return [self._public_row(row) for row in rows]

    def get_today_for_student(
        self,
        klass: str,
        profile: Optional[str],
    ) -> Dict:
        today = date.today()
        day_name = DAY_NAMES[today.weekday()]

        return {
            "date": today.isoformat(),
            "day": day_name,
            "items": self.get_student_schedule(
                klass,
                profile,
                day_name,
            ),
        }

    def get_today_for_teacher(self, fio: str) -> Dict:
        today = date.today()
        day_name = DAY_NAMES[today.weekday()]

        return {
            "date": today.isoformat(),
            "day": day_name,
            "items": self.get_teacher_schedule(
                fio,
                day_name,
            ),
        }

    def reload(self) -> None:
        self._load_schedule()