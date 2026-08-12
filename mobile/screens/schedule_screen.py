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

from mobile.services.api import ApiError, get_week_schedule


DAYS = [
    ("Пн", "Понедельник"),
    ("Вт", "Вторник"),
    ("Ср", "Среда"),
    ("Чт", "Четверг"),
    ("Пт", "Пятница"),
]

KV = '''
#:import dp kivy.metrics.dp

<DayButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: (1, 1, 1, 1) if self.active else (0.16, 0.14, 0.20, 1)
    bold: True
    font_size: "18sp"
    canvas.before:
        Color:
            rgba: (0.40, 0.24, 0.80, 1) if self.active else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<ScheduleLessonRow>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(80)
    padding: dp(6), dp(5)
    spacing: dp(10)
    canvas.after:
        Color:
            rgba: 0.88, 0.87, 0.91, 1
        Rectangle:
            pos: self.x + dp(4), self.y
            size: self.width - dp(8), dp(1)

    LessonNumber:
        number: root.number

    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.58
        spacing: dp(1)
        Label:
            text: root.subject
            font_size: "18sp"
            bold: True
            color: 0.10, 0.08, 0.16, 1
            halign: "left"
            valign: "middle"
            text_size: self.size
        Label:
            text: root.teacher
            font_size: "14sp"
            color: 0.42, 0.40, 0.47, 1
            halign: "left"
            valign: "middle"
            text_size: self.size

    BoxLayout:
        orientation: "vertical"
        size_hint_x: 0.30
        Label:
            text: root.time
            font_size: "14sp"
            bold: True
            color: 0.34, 0.20, 0.70, 1
            halign: "right"
            valign: "middle"
            text_size: self.size
        Label:
            text: root.room
            font_size: "14sp"
            color: 0.42, 0.40, 0.47, 1
            halign: "right"
            valign: "middle"
            text_size: self.size

<LessonNumber>:
    size_hint: None, None
    size: dp(44), dp(44)
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

<ScheduleScreen>:
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
                text: "← Назад"
                size_hint_x: None
                width: dp(110)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.35, 0.22, 0.72, 1
                bold: True
                on_release: root.go_home()
            Widget:
            Button:
                text: "↻"
                size_hint_x: None
                width: dp(42)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.35, 0.22, 0.72, 1
                font_size: "22sp"
                on_release: root.load_schedule()

        ScrollView:
            do_scroll_x: False
            bar_width: 0
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
                        text: "Расписание"
                        size_hint_y: None
                        height: dp(48)
                        font_size: "30sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                    Label:
                        id: user_label
                        text: ""
                        size_hint_y: None
                        height: dp(26)
                        font_size: "16sp"
                        color: 0.42, 0.40, 0.47, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                    BoxLayout:
                        size_hint_y: None
                        height: dp(58)
                        spacing: dp(9)
                        DayButton:
                            id: mon_button
                            text: "Пн"
                            active: False
                            on_release: root.select_day("Понедельник")
                        DayButton:
                            id: tue_button
                            text: "Вт"
                            active: False
                            on_release: root.select_day("Вторник")
                        DayButton:
                            id: wed_button
                            text: "Ср"
                            active: False
                            on_release: root.select_day("Среда")
                        DayButton:
                            id: thu_button
                            text: "Чт"
                            active: False
                            on_release: root.select_day("Четверг")
                        DayButton:
                            id: fri_button
                            text: "Пт"
                            active: False
                            on_release: root.select_day("Пятница")

                    Label:
                        id: selected_day_label
                        text: ""
                        size_hint_y: None
                        height: dp(34)
                        font_size: "23sp"
                        bold: True
                        color: 0.10, 0.08, 0.16, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size

                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: max(dp(100), lesson_list.minimum_height + dp(18))
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
                        id: status_label
                        text: ""
                        size_hint_y: None
                        height: dp(28)
                        font_size: "15sp"
                        color: 0.50, 0.28, 0.70, 1
                        halign: "center"
                        valign: "middle"
                        text_size: self.size
'''

Builder.load_string(KV)


class DayButton(Button):
    active = BooleanProperty(False)


class LessonNumber(Label):
    number = StringProperty("")


class ScheduleLessonRow(BoxLayout):
    number = StringProperty("")
    subject = StringProperty("")
    teacher = StringProperty("")
    time = StringProperty("")
    room = StringProperty("")


class ScheduleScreen(Screen):
    selected_day = StringProperty("Понедельник")

    def on_enter(self, *args):
        self.fill_user_data()
        if not self.selected_day:
            self.selected_day = self.default_day()
        self.select_day(self.selected_day)

    def fill_user_data(self):
        user = MDApp.get_running_app().current_user or {}
        parts = [user.get("fio") or "Пользователь", user.get("klass") or ""]
        if user.get("profile"):
            parts.append(user["profile"])
        self.ids.user_label.text = " • ".join(part for part in parts if part)

    @staticmethod
    def default_day():
        index = datetime.now().weekday()
        return DAYS[index][1] if index < 5 else "Понедельник"

    def select_day(self, day):
        self.selected_day = day
        self.ids.selected_day_label.text = day
        button_map = {
            "Понедельник": self.ids.mon_button,
            "Вторник": self.ids.tue_button,
            "Среда": self.ids.wed_button,
            "Четверг": self.ids.thu_button,
            "Пятница": self.ids.fri_button,
        }
        for day_name, button in button_map.items():
            button.active = day_name == day
        self.load_schedule()

    def load_schedule(self):
        user = MDApp.get_running_app().current_user or {}
        self.ids.status_label.text = "Загружаем расписание..."
        try:
            result = get_week_schedule(
                self.selected_day,
                user.get("role", ""),
                klass=user.get("klass", ""),
                profile=user.get("profile", ""),
                fio=user.get("fio", ""),
            )
            items = result.get("items", []) if isinstance(result, dict) else result
            self.render_lessons(items)
            self.ids.status_label.text = "" if items else "На этот день уроков нет"
        except (ApiError, Exception) as error:
            self.render_lessons([])
            self.ids.status_label.text = str(error)
            toast(str(error))

    def render_lessons(self, items):
        container = self.ids.lesson_list
        container.clear_widgets()
        for index, item in enumerate(items or [], 1):
            if not isinstance(item, dict):
                continue
            container.add_widget(ScheduleLessonRow(
                number=str(item.get("num") or item.get("number") or index),
                subject=str(item.get("name") or item.get("subject") or "Урок"),
                teacher=str(item.get("teacher") or ""),
                time=str(item.get("time") or ""),
                room=str(item.get("room") or item.get("cabinet") or ""),
            ))

    def go_home(self):
        self.manager.current = "home"