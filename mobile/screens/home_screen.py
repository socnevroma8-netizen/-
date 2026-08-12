from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.toast import toast

from mobile.services.api import ApiError, get_today_schedule


KV = '''
#:import dp kivy.metrics.dp

<PrimaryButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "19sp"
    bold: True
    canvas.before:
        Color:
            rgba: 0.40, 0.24, 0.80, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<LessonRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(76)
    padding: dp(6), dp(5)
    spacing: dp(10)

    NumberCircle:
        number: root.number

    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.58
        spacing: dp(1)
        Label:
            text: root.subject
            font_size: "17sp"
            bold: True
            color: 0.10, 0.08, 0.16, 1
            halign: "left"
            valign: "middle"
            text_size: self.size
        Label:
            text: root.teacher
            font_size: "13sp"
            color: 0.42, 0.40, 0.47, 1
            halign: "left"
            valign: "middle"
            text_size: self.size

    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.30
        Label:
            text: root.time
            font_size: "13sp"
            bold: True
            color: 0.34, 0.20, 0.70, 1
            halign: "right"
            valign: "middle"
            text_size: self.size
        Label:
            text: root.room
            font_size: "13sp"
            color: 0.42, 0.40, 0.47, 1
            halign: "right"
            valign: "middle"
            text_size: self.size

<NumberCircle>:
    size_hint: None, None
    size: dp(43), dp(43)
    text: root.number
    font_size: "17sp"
    bold: True
    color: 1, 1, 1, 1
    halign: "center"
    valign: "middle"
    text_size: self.size
    canvas.before:
        Color:
            rgba: 0.40, 0.24, 0.80, 1
        Ellipse:
            pos: self.pos
            size: self.size

<HomeScreen>:
    canvas.before:
        Color:
            rgba: 0.93, 0.90, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(18), dp(12), dp(18), dp(8)
        spacing: dp(8)

        BoxLayout:
            size_hint_y: None
            height: dp(42)
            Button:
                text: "← Выйти"
                size_hint_x: None
                width: dp(105)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.35, 0.22, 0.72, 1
                bold: True
                on_release: root.logout()
            Widget:
            Button:
                text: "↻"
                size_hint_x: None
                width: dp(42)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.35, 0.22, 0.72, 1
                font_size: "22sp"
                on_release: root.refresh()

        ScrollView:
            do_scroll_x: False
            bar_width: dp(6)
            AnchorLayout:
                anchor_x: "center"
                anchor_y: "top"
                size_hint_y: None
                height: content.height
                GridLayout:
                    id: content
                    cols: 1
                    size_hint: None, None
                    width: min(root.width - dp(36), dp(560))
                    height: self.minimum_height
                    spacing: dp(14)
                    padding: 0, dp(4), 0, dp(24)

                    Label:
                        text: "Гимназия Доброграда"
                        size_hint_y: None
                        height: dp(48)
                        font_size: "28sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: dp(82)
                        padding: dp(8), dp(6)
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(26)]
                        Label:
                            id: user_name
                            text: ""
                            font_size: "18sp"
                            bold: True
                            color: 0.10, 0.08, 0.16, 1
                        Label:
                            id: user_info
                            text: ""
                            font_size: "15sp"
                            color: 0.42, 0.40, 0.47, 1

                    Label:
                        text: "Расписание на сегодня"
                        size_hint_y: None
                        height: dp(38)
                        font_size: "25sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "left"
                        text_size: self.size

                    Label:
                        id: date_label
                        text: ""
                        size_hint_y: None
                        height: dp(24)
                        font_size: "16sp"
                        color: 0.42, 0.40, 0.47, 1
                        halign: "left"
                        text_size: self.size

                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: max(dp(90), lesson_list.minimum_height + dp(18))
                        padding: dp(12), dp(5)
                        canvas.before:
                            Color:
                                rgba: 1, 1, 1, 1
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [dp(28)]
                        BoxLayout:
                            id: lesson_list
                            orientation: "vertical"
                            size_hint_y: None
                            height: self.minimum_height

                    Label:
                        text: "Меню"
                        size_hint_y: None
                        height: dp(42)
                        font_size: "27sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "left"
                        text_size: self.size


                    PrimaryButton:
                        text: "База пользователей"
                        size_hint_y: None
                        height: dp(64) if root.admin_visible else 0
                        opacity: 1 if root.admin_visible else 0
                        disabled: not root.admin_visible
                        on_release: root.open_admin()

                    PrimaryButton:
                        text: "Расписание"
                        size_hint_y: None
                        height: dp(64)
                        on_release: root.open_schedule()

                    PrimaryButton:
                        text: "Напоминания"
                        size_hint_y: None
                        height: dp(64)
                        on_release: root.open_reminders()

                    PrimaryButton:
                        text: "Преподаватели"
                        size_hint_y: None
                        height: dp(64)
                        on_release: root.open_teachers()

                    PrimaryButton:
                        text: "Трансфер"
                        size_hint_y: None
                        height: dp(64)
                        on_release: root.open_transfers()
'''

Builder.load_string(KV)


class PrimaryButton(Button):
    pass


class NumberCircle(Label):
    number = StringProperty("")


class LessonRow(BoxLayout):
    number = StringProperty("")
    subject = StringProperty("")
    teacher = StringProperty("")
    time = StringProperty("")
    room = StringProperty("")


class HomeScreen(Screen):
    admin_visible = BooleanProperty(False)

    def on_enter(self, *args):
        self.fill_user_data()
        self.refresh(False)

    def fill_user_data(self):
        app = MDApp.get_running_app()
        user = app.current_user or {}
        self.admin_visible = bool(user.get("admin", False))

        self.ids.user_name.text = user.get("fio") or "Пользователь"
        role = {
            "student": "ученик",
            "teacher": "педагог",
        }.get(user.get("role"), user.get("role", ""))
        values = [role, user.get("klass", ""), user.get("profile", "")]

        if self.admin_visible:
            values.insert(0, "администратор")

        self.ids.user_info.text = " • ".join(
            value for value in values if value
        )
        self.ids.date_label.text = self.today_label()

    def today_label(self):
        months = [
            "января", "февраля", "марта", "апреля",
            "мая", "июня", "июля", "августа",
            "сентября", "октября", "ноября", "декабря",
        ]
        days = [
            "Понедельник", "Вторник", "Среда", "Четверг",
            "Пятница", "Суббота", "Воскресенье",
        ]
        now = datetime.now()
        return (
            f"{now.day} {months[now.month - 1]} "
            f"{now.year} • {days[now.weekday()]}"
        )

    def refresh(self, show_toast=True):
        user = MDApp.get_running_app().current_user or {}
        try:
            result = get_today_schedule(
                user.get("role", ""),
                klass=user.get("klass", ""),
                profile=user.get("profile", ""),
                fio=user.get("fio", ""),
            )
            items = (
                result.get("items", [])
                if isinstance(result, dict)
                else result
            )
            self.render_lessons(items)
            if show_toast:
                toast("Расписание обновлено")
        except Exception as error:
            self.render_lessons([])
            if show_toast:
                toast(str(error))

    def render_lessons(self, items):
        container = self.ids.lesson_list
        container.clear_widgets()

        for index, item in enumerate(items or [], 1):
            if not isinstance(item, dict):
                continue

            container.add_widget(
                LessonRow(
                    number=str(
                        item.get("num")
                        or item.get("number")
                        or index
                    ),
                    subject=str(
                        item.get("name")
                        or item.get("subject")
                        or "Урок"
                    ),
                    teacher=str(item.get("teacher") or ""),
                    time=str(item.get("time") or ""),
                    room=str(
                        item.get("room")
                        or item.get("cabinet")
                        or ""
                    ),
                )
            )

    def open_schedule(self):
        self.manager.current = "schedule"

    def open_reminders(self):
        self.manager.current = "reminders"

    def open_teachers(self):
        self.manager.current = "teachers"

    def open_transfers(self):
        self.manager.current = "transfer"

    def open_users(self):
        self.manager.current = "users"

    def open_admin(self):
        self.manager.current = "admin"

    def logout(self):
        MDApp.get_running_app().logout()