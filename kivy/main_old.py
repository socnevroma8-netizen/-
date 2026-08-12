import requests

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

print("=== NEW MAIN.PY STARTED ===")
API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5
DAYS = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница")


class BaseScreen(Screen):
    def _set_label_wrap(self, label):
        label.bind(width=lambda instance, value: setattr(instance, "text_size", (value, None)))

    def _request(self, method, endpoint, params=None):
        try:
            resp = requests.request(
                method=method,
                url=f"{API_BASE_URL}{endpoint}",
                params=params or {},
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            return None, f"Ошибка соединения: {e}"

        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.status_code != 200:
            if isinstance(data, dict):
                return None, data.get("detail", f"HTTP {resp.status_code}")
            return None, f"HTTP {resp.status_code}"

        return data, None


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(
            text="Цифровая система школы",
            font_size=28,
            size_hint=(1, None),
            height=50,
        )
        root.add_widget(title)

        subtitle = Label(
            text="Выберите роль пользователя",
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(subtitle)

        student_btn = Button(text="Ученик", size_hint=(1, None), height=50)
        teacher_btn = Button(text="Педагог", size_hint=(1, None), height=50)
        admin_btn = Button(text="Администратор", size_hint=(1, None), height=50)

        student_btn.bind(on_press=lambda *_: self.go_to("student"))
        teacher_btn.bind(on_press=lambda *_: self.go_to("teacher"))
        admin_btn.bind(on_press=lambda *_: self.go_to("admin"))

        root.add_widget(student_btn)
        root.add_widget(teacher_btn)
        root.add_widget(admin_btn)

        self.add_widget(root)

    def go_to(self, screen_name):
        self.manager.current = screen_name


class StudentScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.student_info = None

        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        title = Label(
            text="Кабинет ученика",
            font_size=24,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(title)

        self.username_input = TextInput(
            hint_text="Логин",
            multiline=False,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Пароль",
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.password_input)

        login_btn = Button(text="Войти", size_hint=(1, None), height=40)
        login_btn.bind(on_press=self.on_login_pressed)
        root.add_widget(login_btn)

        self.result_label = Label(
            text="",
            size_hint=(1, None),
            height=80,
            halign="left",
            valign="middle",
        )
        self._set_label_wrap(self.result_label)
        root.add_widget(self.result_label)

        self.day_spinner = Spinner(
            text="Выберите день",
            values=DAYS,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.day_spinner)

        schedule_btn = Button(text="Показать расписание", size_hint=(1, None), height=40)
        schedule_btn.bind(on_press=self.on_schedule_pressed)
        root.add_widget(schedule_btn)

        self.schedule_label = Label(
            text="",
            size_hint=(1, 1),
            halign="left",
            valign="top",
        )
        self._set_label_wrap(self.schedule_label)
        root.add_widget(self.schedule_label)

        back_btn = Button(text="Назад", size_hint=(1, None), height=40)
        back_btn.bind(on_press=lambda *_: self.go_home())
        root.add_widget(back_btn)

        self.add_widget(root)

    def go_home(self):
        self.clear_fields()
        self.manager.current = "home"

    def clear_fields(self):
        self.username_input.text = ""
        self.password_input.text = ""
        self.day_spinner.text = "Выберите день"
        self.result_label.text = ""
        self.schedule_label.text = ""
        self.student_info = None

    def on_login_pressed(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.result_label.text = "Введите логин и пароль"
            return

        self.schedule_label.text = ""
        data, error = self._request("POST", "/api/login/student", {"username": username, "password": password})
        if error:
            self.student_info = None
            self.result_label.text = error
            return

        fio = data.get("fio", "")
        klass = data.get("klass", "")
        profile = data.get("profile", "")
        admin = data.get("admin", False)

        self.student_info = {"fio": fio, "klass": klass, "profile": profile, "admin": admin}

        profile_text = f", профиль: {profile}" if profile else ""
        admin_text = " (администратор)" if admin else ""
        self.result_label.text = f"{fio}\nКласс: {klass}{profile_text}{admin_text}"

    def on_schedule_pressed(self, instance):
        if not self.student_info:
            self.schedule_label.text = "Сначала войдите как ученик"
            return

        day = self.day_spinner.text.strip()
        if day == "Выберите день":
            self.schedule_label.text = "Выберите день"
            return

        data, error = self._request(
            "GET",
            "/api/schedule/student",
            {
                "klass": self.student_info["klass"],
                "profile": self.student_info["profile"],
                "day": day,
            },
        )
        if error:
            self.schedule_label.text = error
            return

        if not data:
            self.schedule_label.text = "На этот день уроков нет"
            return

        lines = []
        for lesson in data:
            num = lesson.get("lesson_number", "")
            time_ = lesson.get("time", "")
            subj = lesson.get("subject", "")
            room = lesson.get("room", "")
            lines.append(f"{num}. {time_} — {subj} (каб. {room})")

        self.schedule_label.text = "\n".join(lines)


class TeacherScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.teacher_info = None

        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        title = Label(
            text="Кабинет педагога",
            font_size=24,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(title)

        self.username_input = TextInput(
            hint_text="Логин",
            multiline=False,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Пароль",
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.password_input)

        login_btn = Button(text="Войти", size_hint=(1, None), height=40)
        login_btn.bind(on_press=self.on_login_pressed)
        root.add_widget(login_btn)

        self.result_label = Label(
            text="",
            size_hint=(1, None),
            height=80,
            halign="left",
            valign="middle",
        )
        self._set_label_wrap(self.result_label)
        root.add_widget(self.result_label)

        self.day_spinner = Spinner(
            text="Выберите день",
            values=DAYS,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.day_spinner)

        schedule_btn = Button(text="Показать расписание", size_hint=(1, None), height=40)
        schedule_btn.bind(on_press=self.on_schedule_pressed)
        root.add_widget(schedule_btn)

        self.schedule_label = Label(
            text="",
            size_hint=(1, 1),
            halign="left",
            valign="top",
        )
        self._set_label_wrap(self.schedule_label)
        root.add_widget(self.schedule_label)

        back_btn = Button(text="Назад", size_hint=(1, None), height=40)
        back_btn.bind(on_press=lambda *_: self.go_home())
        root.add_widget(back_btn)

        self.add_widget(root)

    def go_home(self):
        self.clear_fields()
        self.manager.current = "home"

    def clear_fields(self):
        self.username_input.text = ""
        self.password_input.text = ""
        self.day_spinner.text = "Выберите день"
        self.result_label.text = ""
        self.schedule_label.text = ""
        self.teacher_info = None

    def on_login_pressed(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.result_label.text = "Введите логин и пароль"
            return

        self.schedule_label.text = ""
        data, error = self._request("POST", "/api/login/teacher", {"username": username, "password": password})
        if error:
            self.teacher_info = None
            self.result_label.text = error
            return

        fio = data.get("fio", "")
        subject = data.get("subject", "")
        room = data.get("room", "")
        admin = data.get("admin", False)

        self.teacher_info = {"fio": fio, "subject": subject, "room": room, "admin": admin}

        admin_text = " (администратор)" if admin else ""
        self.result_label.text = f"{fio}\nПредмет: {subject}, кабинет: {room}{admin_text}"

    def on_schedule_pressed(self, instance):
        if not self.teacher_info:
            self.schedule_label.text = "Сначала войдите как педагог"
            return

        day = self.day_spinner.text.strip()
        if day == "Выберите день":
            self.schedule_label.text = "Выберите день"
            return

        data, error = self._request(
            "GET",
            "/api/schedule/teacher",
            {"fio": self.teacher_info["fio"], "day": day},
        )
        if error:
            self.schedule_label.text = error
            return

        if not data:
            self.schedule_label.text = "На этот день уроков нет"
            return

        lines = []
        for lesson in data:
            num = lesson.get("lesson_number", "")
            time_ = lesson.get("time", "")
            subj = lesson.get("subject", "")
            room = lesson.get("room", "")
            klass = lesson.get("klass", "")
            profile = lesson.get("profile", "")
            profile_text = f", профиль: {profile}" if profile else ""
            lines.append(f"{num}. {time_} — {subj} ({klass}{profile_text}, каб. {room})")

        self.schedule_label.text = "\n".join(lines)


class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.admin_info = None

        root = BoxLayout(orientation="vertical", padding=20, spacing=10)

        title = Label(
            text="Панель администратора",
            font_size=24,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(title)

        self.username_input = TextInput(
            hint_text="Логин администратора",
            multiline=False,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.username_input)

        self.password_input = TextInput(
            hint_text="Пароль",
            multiline=False,
            password=True,
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(self.password_input)

        login_btn = Button(text="Войти", size_hint=(1, None), height=40)
        login_btn.bind(on_press=self.on_login_pressed)
        root.add_widget(login_btn)

        self.result_label = Label(
            text="",
            size_hint=(1, None),
            height=80,
            halign="left",
            valign="middle",
        )
        self._set_label_wrap(self.result_label)
        root.add_widget(self.result_label)

        btn_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=40,
            spacing=10,
        )

        self.students_btn = Button(text="Список учеников", disabled=True)
        self.teachers_btn = Button(text="Список педагогов", disabled=True)
        clear_btn = Button(text="Очистить")

        self.students_btn.bind(on_press=self.show_students)
        self.teachers_btn.bind(on_press=self.show_teachers)
        clear_btn.bind(on_press=self.clear_output)

        btn_row.add_widget(self.students_btn)
        btn_row.add_widget(self.teachers_btn)
        btn_row.add_widget(clear_btn)

        root.add_widget(btn_row)

        self.data_label = Label(
            text="",
            size_hint=(1, 1),
            halign="left",
            valign="top",
        )
        self._set_label_wrap(self.data_label)
        root.add_widget(self.data_label)

        back_btn = Button(text="Назад", size_hint=(1, None), height=40)
        back_btn.bind(on_press=lambda *_: self.go_home())
        root.add_widget(back_btn)

        self.add_widget(root)

    def go_home(self):
        self.clear_fields()
        self.manager.current = "home"

    def clear_fields(self):
        self.username_input.text = ""
        self.password_input.text = ""
        self.result_label.text = ""
        self.data_label.text = ""
        self.admin_info = None
        self.students_btn.disabled = True
        self.teachers_btn.disabled = True

    def clear_output(self, instance=None):
        self.data_label.text = ""

    def on_login_pressed(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        if not username or not password:
            self.result_label.text = "Введите логин и пароль"
            return

        self.data_label.text = ""
        data, error = self._request("POST", "/api/login/admin", {"username": username, "password": password})
        if error:
            self.admin_info = None
            self.students_btn.disabled = True
            self.teachers_btn.disabled = True
            self.result_label.text = error
            return

        fio = data.get("fio", "")
        klass = data.get("klass", "")
        profile = data.get("profile", "")
        admin = bool(data.get("admin", False))

        if not admin:
            self.admin_info = None
            self.students_btn.disabled = True
            self.teachers_btn.disabled = True
            self.result_label.text = "У пользователя нет прав администратора"
            return

        self.admin_info = {
            "fio": fio,
            "klass": klass,
            "profile": profile,
            "admin": admin,
            "username": username,
            "password": password,
        }

        self.students_btn.disabled = False
        self.teachers_btn.disabled = False

        profile_text = f", профиль: {profile}" if profile else ""
        self.result_label.text = f"{fio}\nКласс: {klass}{profile_text} (администратор)"

    def show_students(self, instance):
        if not self.admin_info:
            self.data_label.text = "Сначала войдите как администратор"
            return

        data, error = self._request(
            "GET",
            "/api/admin/students",
            {"username": self.admin_info["username"], "password": self.admin_info["password"]},
        )
        if error:
            self.data_label.text = error
            return

        if not data:
            self.data_label.text = "В базе пока нет учеников"
            return

        lines = ["Ученики школы:\n"]
        for s in data:
            fio = s.get("fio", "")
            klass = s.get("klass", "")
            profile = s.get("profile", "")
            login = s.get("login", "")
            admin_flag = s.get("is_admin", False)

            admin_mark = " [админ]" if admin_flag else ""
            profile_text = f", профиль: {profile}" if profile else ""
            lines.append(f"{fio} — {klass}{profile_text}, логин: {login}{admin_mark}")

        self.data_label.text = "\n".join(lines)

    def show_teachers(self, instance):
        if not self.admin_info:
            self.data_label.text = "Сначала войдите как администратор"
            return

        data, error = self._request(
            "GET",
            "/api/admin/teachers",
            {"username": self.admin_info["username"], "password": self.admin_info["password"]},
        )
        if error:
            self.data_label.text = error
            return

        if not data:
            self.data_label.text = "В базе пока нет педагогов"
            return

        lines = ["Педагоги школы:\n"]
        for t in data:
            fio = t.get("fio", "")
            subject = t.get("subject", "")
            room = t.get("room", "")
            login = t.get("login", "")
            admin_flag = t.get("is_admin", False)

            admin_mark = " [админ]" if admin_flag else ""
            lines.append(f"{fio} — {subject}, кабинет: {room}, логин: {login}{admin_mark}")

        self.data_label.text = "\n".join(lines)


class ScheduleApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(StudentScreen(name="student"))
        sm.add_widget(TeacherScreen(name="teacher"))
        sm.add_widget(AdminScreen(name="admin"))
        sm.current = "home"
        return sm


if __name__ == "__main__":
    ScheduleApp().run()