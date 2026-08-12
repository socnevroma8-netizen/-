from dataclasses import dataclass


@dataclass
class StudentDTO:
    fio: str
    klass: str
    profile: str
    login: str
    is_admin: bool = False


@dataclass
class TeacherDTO:
    fio: str
    subject: str
    room: str
    login: str
    class_guide: str = ""
    is_admin: bool = False


@dataclass
class LessonDTO:
    klass_profile: str
    day: str
    lesson_number: int
    time: str
    subject: str
    teacher: str
    room: str