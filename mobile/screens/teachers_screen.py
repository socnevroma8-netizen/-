import os

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.toast import toast

from mobile.services.api import ApiError, get_teachers


KV = """
#:import dp kivy.metrics.dp

<TeachersScreen>:
    canvas.before:
        Color:
            rgba: 0.93, 0.90, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(14), dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(42)

            Button:
                text: "← Назад"
                size_hint_x: None
                width: dp(102)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.32, 0.18, 0.70, 1
                bold: True
                on_release: root.go_back()

            Widget:

        ScrollView:
            do_scroll_x: False
            bar_width: 0

            BoxLayout:
                id: content
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(14)
                padding: dp(8), dp(6), dp(8), dp(24)
"""

Builder.load_string(KV)


class WhiteCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(22)],
            )
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


class TeachersScreen(Screen):
    def on_pre_enter(self, *args):
        self.render_teachers()

    def make_label(self, text, height, font_size, color, bold=False, halign="center"):
        label = Label(
            text=str(text),
            size_hint_y=None,
            height=dp(height),
            font_size=font_size,
            color=color,
            bold=bold,
            halign=halign,
            valign="middle",
            text_size=(0, None),
        )
        label.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        return label

    def load_teachers(self):
        try:
            data = get_teachers()
            if isinstance(data, dict):
                teachers = data.get("items", [])
            elif isinstance(data, list):
                teachers = data
            else:
                teachers = []

            return [item for item in teachers if isinstance(item, dict)]
        except ApiError as error:
            toast(str(error))
            return []
        except Exception as error:
            toast(f"Ошибка загрузки учителей: {error}")
            return []

    @staticmethod
    def teacher_name(teacher):
        return (
            teacher.get("fio")
            or teacher.get("name")
            or teacher.get("full_name")
            or teacher.get("fullName")
            or "Учитель"
        )

    @staticmethod
    def teacher_subject(teacher):
        return (
            teacher.get("subject")
            or teacher.get("subjects")
            or teacher.get("предмет")
            or "Предмет не указан"
        )

    def teacher_card(self, teacher):
        details = []
        email = teacher.get("email") or teacher.get("mail") or ""
        phone = teacher.get("phone") or teacher.get("telephone") or ""
        room = teacher.get("room") or teacher.get("кабинет") or ""

        if email:
            details.append(f"Почта: {email}")
        if phone:
            details.append(f"Телефон: {phone}")
        if room:
            details.append(f"Кабинет: {room}")

        detail_text = "\n".join(details) if details else "Контактная информация пока не указана"
        detail_height = max(48, 22 * max(1, len(details)))

        card = WhiteCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(76 + detail_height),
            padding=(dp(18), dp(13)),
            spacing=dp(3),
        )
        card.add_widget(self.make_label(self.teacher_name(teacher), 33, "19sp", (0.10, 0.08, 0.16, 1), True, "left"))
        card.add_widget(self.make_label(self.teacher_subject(teacher), 27, "16sp", (0.38, 0.22, 0.72, 1), False, "left"))
        card.add_widget(self.make_label(detail_text, detail_height, "14sp", (0.34, 0.32, 0.40, 1), False, "left"))
        return card

    def render_teachers(self, *_):
        content = self.ids.content
        content.clear_widgets()

        content.add_widget(self.make_label("Учителя", 54, "30sp", (0.10, 0.08, 0.16, 1), True))

        search = TextInput(
            hint_text="Поиск по имени или предмету",
            multiline=False,
            size_hint_y=None,
            height=dp(52),
            font_size="16sp",
            padding=[dp(16), dp(13)],
            background_normal="",
            background_active="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0.12, 0.10, 0.18, 1),
            hint_text_color=(0.50, 0.47, 0.60, 1),
        )
        search.bind(text=self.filter_teachers)
        self.search_input = search
        content.add_widget(search)

        self.cards_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
        )
        self.cards_box.bind(minimum_height=self.cards_box.setter("height"))
        content.add_widget(self.cards_box)

        self.teachers = self.load_teachers()
        self.show_teacher_cards(self.teachers)

    def filter_teachers(self, instance, value):
        query = value.strip().lower()
        teachers = self.teachers
        if query:
            teachers = [
                teacher for teacher in teachers
                if query in self.teacher_name(teacher).lower()
                or query in str(self.teacher_subject(teacher)).lower()
            ]
        self.show_teacher_cards(teachers)

    def show_teacher_cards(self, teachers):
        self.cards_box.clear_widgets()

        if not teachers:
            empty = WhiteCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(112),
                padding=dp(14),
            )
            empty.add_widget(self.make_label("Учителя пока не добавлены", 34, "18sp", (0.30, 0.28, 0.36, 1), True))
            empty.add_widget(self.make_label("Список загружается с сервера", 30, "14sp", (0.42, 0.40, 0.48, 1)))
            self.cards_box.add_widget(empty)
            return

        for teacher in teachers:
            self.cards_box.add_widget(self.teacher_card(teacher))

    def go_back(self):
        self.manager.current = "home"