from pathlib import Path

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager

from mobile.services.api import ApiError, create_user, upload_schedule


KV = '''
#:import dp kivy.metrics.dp

<AdminRoundedButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "18sp"
    bold: True
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<ChoiceButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: (1, 1, 1, 1) if self.selected else (0.40, 0.24, 0.80, 1)
    font_size: "17sp"
    bold: True
    canvas.before:
        Color:
            rgba: (0.54, 0.39, 0.88, 1) if self.selected else (0.95, 0.93, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<AdminInput>:
    multiline: False
    readonly: False
    disabled: False
    write_tab: False
    font_size: "17sp"
    padding: dp(18), dp(14)
    foreground_color: 0.12, 0.10, 0.18, 1
    hint_text_color: 0.55, 0.52, 0.64, 1
    cursor_color: 0.42, 0.27, 0.84, 1
    background_normal: ""
    background_active: ""
    background_color: 0, 0, 0, 0

    canvas.before:
        Color:
            rgba: 0.96, 0.95, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

        Color:
            rgba: (0.42, 0.27, 0.84, 1) if self.focus else (0.84, 0.81, 0.92, 1)
        Line:
            width: 1.2
            rounded_rectangle: self.x, self.y, self.width, self.height, self.height / 2

<WhiteCard>:
    orientation: "vertical"
    size_hint_y: None
    padding: dp(18), dp(16)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(28)]

<AdminScreen>:
    canvas.before:
        Color:
            rgba: 0.93, 0.90, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(16), dp(10), dp(16), dp(8)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(46)
            Button:
                text: "← Назад"
                size_hint_x: None
                width: dp(116)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.36, 0.22, 0.73, 1
                font_size: "16sp"
                bold: True
                on_release: root.go_home()
            Widget:

        ScrollView:
            do_scroll_x: False
            bar_width: dp(6)

            AnchorLayout:
                anchor_x: "center"
                anchor_y: "top"
                size_hint_y: None
                height: content.height

                BoxLayout:
                    id: content
                    orientation: "vertical"
                    size_hint: None, None
                    width: min(root.width - dp(32), dp(620))
                    height: self.minimum_height
                    spacing: dp(16)
                    padding: 0, dp(6), 0, dp(30)

                    Label:
                        text: "База пользователей"
                        size_hint_y: None
                        height: dp(52)
                        font_size: "31sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                    Label:
                        text: "Основная роль: ученик или педагог. Админ — дополнительное право доступа."
                        size_hint_y: None
                        height: dp(48)
                        font_size: "15sp"
                        color: 0.42, 0.40, 0.47, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.width, None

                    WhiteCard:
                        height: role_card.minimum_height + dp(32)
                        BoxLayout:
                            id: role_card
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(10)

                            Label:
                                text: "Новый пользователь"
                                size_hint_y: None
                                height: dp(32)
                                font_size: "25sp"
                                bold: True
                                color: 0.10, 0.08, 0.16, 1
                                halign: "left"
                                text_size: self.size

                            Label:
                                text: "Основная роль"
                                size_hint_y: None
                                height: dp(26)
                                font_size: "17sp"
                                bold: True
                                color: 0.20, 0.18, 0.26, 1
                                halign: "left"
                                text_size: self.size

                            BoxLayout:
                                size_hint_y: None
                                height: dp(54)
                                spacing: dp(12)
                                ChoiceButton:
                                    text: "Ученик"
                                    selected: root.role == "student"
                                    on_release: root.set_role("student")
                                ChoiceButton:
                                    text: "Педагог"
                                    selected: root.role == "teacher"
                                    on_release: root.set_role("teacher")

                            ChoiceButton:
                                text: "Администратор"
                                size_hint_y: None
                                height: dp(54)
                                selected: root.is_admin
                                on_release: root.toggle_admin()

                            AdminInput:
                                id: fio_input
                                hint_text: "ФИО"
                                size_hint_y: None
                                height: dp(58)

                            AdminInput:
                                id: klass_input
                                hint_text: "Класс, например 10Б"
                                size_hint_y: None
                                height: dp(58)
                                opacity: 1 if root.role == "student" else 0
                                disabled: root.role != "student"

                            AdminInput:
                                id: profile_input
                                hint_text: "Профиль, если есть"
                                size_hint_y: None
                                height: dp(58)
                                opacity: 1 if root.role == "student" else 0
                                disabled: root.role != "student"

                            AdminInput:
                                id: subject_input
                                hint_text: "Предмет"
                                size_hint_y: None
                                height: dp(58)
                                opacity: 1 if root.role == "teacher" else 0
                                disabled: root.role != "teacher"

                            AdminInput:
                                id: cabinet_input
                                hint_text: "Кабинет"
                                size_hint_y: None
                                height: dp(58)
                                opacity: 1 if root.role == "teacher" else 0
                                disabled: root.role != "teacher"

                            AdminInput:
                                id: classroom_input
                                hint_text: "Классное руководство"
                                size_hint_y: None
                                height: dp(58)
                                opacity: 1 if root.role == "teacher" else 0
                                disabled: root.role != "teacher"

                            AdminInput:
                                id: login_input
                                hint_text: "Логин"
                                size_hint_y: None
                                height: dp(58)

                            AdminInput:
                                id: password_input
                                hint_text: "Пароль"
                                password: True
                                size_hint_y: None
                                height: dp(58)

                            AdminRoundedButton:
                                text: "Добавить пользователя"
                                size_hint_y: None
                                height: dp(64)
                                bg_color: 0.45, 0.28, 0.86, 1
                                on_release: root.save_user()

                    WhiteCard:
                        height: upload_box.minimum_height + dp(32)
                        BoxLayout:
                            id: upload_box
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(10)

                            Label:
                                text: "Обновление расписания"
                                size_hint_y: None
                                height: dp(32)
                                font_size: "25sp"
                                bold: True
                                color: 0.10, 0.08, 0.16, 1
                                halign: "left"
                                text_size: self.size

                            Label:
                                id: schedule_path_label
                                text: "Выберите актуальный файл расписания .xlsx"
                                size_hint_y: None
                                height: dp(40)
                                font_size: "15sp"
                                color: 0.42, 0.40, 0.47, 1
                                halign: "left"
                                valign: "middle"
                                text_size: self.width, None

                            AdminRoundedButton:
                                text: "Выбрать файл .xlsx"
                                size_hint_y: None
                                height: dp(58)
                                bg_color: 0.62, 0.52, 0.89, 1
                                on_release: root.open_file_manager()

                            AdminRoundedButton:
                                text: "Загрузить расписание"
                                size_hint_y: None
                                height: dp(58)
                                bg_color: 0.45, 0.28, 0.86, 1
                                on_release: root.upload_selected_schedule()

                    Label:
                        id: status_label
                        text: ""
                        size_hint_y: None
                        height: dp(34)
                        font_size: "15sp"
                        color: 0.42, 0.24, 0.72, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size
'''

Builder.load_string(KV)


class AdminRoundedButton(Button):
    bg_color = ListProperty([0.45, 0.28, 0.86, 1])


class ChoiceButton(Button):
    selected = BooleanProperty(False)


class AdminInput(TextInput):
    pass


class WhiteCard(BoxLayout):
    pass


class AdminScreen(Screen):
    role = StringProperty("student")
    is_admin = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_schedule_path = None
        self.file_manager = MDFileManager(
            exit_manager=self.close_file_manager,
            select_path=self.select_schedule_path,
        )

    def on_pre_enter(self, *args):
        user = MDApp.get_running_app().current_user or {}
        if not user.get("admin", False):
            toast("Доступ только для администратора")
            self.go_home()

    def set_role(self, role):
        self.role = role

    def toggle_admin(self):
        self.is_admin = not self.is_admin

    def save_user(self):
        ids = self.ids
        fio = ids.fio_input.text.strip()
        login = ids.login_input.text.strip()
        password = ids.password_input.text.strip()

        if not fio or not login or not password:
            self.show_status("Заполните ФИО, логин и пароль", error=True)
            return

        try:
            create_user(
                fio=fio,
                role=self.role,
                login=login,
                password=password,
                klass=ids.klass_input.text.strip(),
                profile=ids.profile_input.text.strip(),
                subject=ids.subject_input.text.strip(),
                cabinet=ids.cabinet_input.text.strip(),
                classroom=ids.classroom_input.text.strip(),
                admin=self.is_admin,
            )
        except ApiError as error:
            self.show_status(str(error), error=True)
            return

        for field_id in (
            "fio_input", "klass_input", "profile_input", "subject_input",
            "cabinet_input", "classroom_input", "login_input", "password_input",
        ):
            ids[field_id].text = ""

        self.show_status("Пользователь успешно создан")
        toast("Пользователь создан")

    def open_file_manager(self):
        self.file_manager.show(str(Path.home()))

    def close_file_manager(self, *_):
        self.file_manager.close()

    def select_schedule_path(self, path):
        self.file_manager.close()
        self.selected_schedule_path = path
        self.ids.schedule_path_label.text = Path(path).name

    def upload_selected_schedule(self):
        path = self.selected_schedule_path
        if not path:
            self.show_status("Сначала выберите файл .xlsx", error=True)
            return

        if not path.lower().endswith(".xlsx"):
            self.show_status("Нужен файл формата .xlsx", error=True)
            return

        try:
            result = upload_schedule(path)
        except ApiError as error:
            self.show_status(str(error), error=True)
            return

        count = result.get("lessons_count") if isinstance(result, dict) else None
        message = "Расписание обновлено"
        if count is not None:
            message += f": {count} уроков"
        self.show_status(message)
        toast(message)

    def show_status(self, message, error=False):
        self.ids.status_label.color = (
            (0.80, 0.18, 0.25, 1)
            if error else (0.42, 0.24, 0.72, 1)
        )
        self.ids.status_label.text = message

    def go_home(self):
        self.manager.current = "home"