import json
import os
from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from kivymd.app import MDApp
from kivymd.toast import toast


KV = """
#:import dp kivy.metrics.dp

<RemindersScreen>:
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
            id: scroll
            do_scroll_x: False
            bar_width: 0
            effect_cls: "ScrollEffect"

            AnchorLayout:
                id: anchor
                anchor_x: "center"
                anchor_y: "top"
                size_hint_y: None
                height: content.height

                BoxLayout:
                    id: content
                    orientation: "vertical"
                    size_hint_x: 0.92
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(14)
                    padding: 0, dp(5), 0, dp(25)
"""

Builder.load_string(KV)


class RoundedButton(Button):
    def __init__(self, purple=False, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1) if purple else (0.32, 0.18, 0.70, 1)
        self.bold = True

        with self.canvas.before:
            self.fill_color = Color(*(0.40, 0.23, 0.80, 1) if purple else (1, 1, 1, 1))
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])

        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


class WhiteCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kivy.graphics import Color, RoundedRectangle

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.shape = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(22)])
        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


class Field(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from kivy.graphics import Color, Line, RoundedRectangle

        self.multiline = kwargs.get("multiline", False)
        self.font_size = "16sp"
        self.padding = [dp(16), dp(13)]
        self.foreground_color = (0.12, 0.10, 0.18, 1)
        self.hint_text_color = (0.50, 0.47, 0.60, 1)

        self.background_normal = ""
        self.background_active = ""
        self.background_color = (0, 0, 0, 0)

        with self.canvas.before:
            Color(0.96, 0.95, 1, 1)
            self.fill_shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)],
            )

            Color(0.84, 0.81, 0.92, 1)
            self.border_line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(15),
                ),
                width=1,
            )

        self.bind(pos=self._update_shape, size=self._update_shape)

    def _update_shape(self, *_):
        self.fill_shape.pos = self.pos
        self.fill_shape.size = self.size

        self.border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(15),
        )


class ReminderCard(WhiteCard):
    def __init__(self, item, delete_callback, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, padding=dp(17), spacing=dp(5), **kwargs)
        self.item = item
        self.delete_callback = delete_callback
        self.height = dp(142 if item.get("text") else 108)

        title_row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(8))
        title = Label(
            text=item.get("title") or "Без темы",
            color=(0.10, 0.08, 0.16, 1),
            font_size="18sp",
            bold=True,
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        title.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        title_row.add_widget(title)

        remove = RoundedButton(text="Удалить", size_hint_x=None, width=dp(82), font_size="12sp")
        remove.fill_color.rgba = (1, 0.88, 0.88, 1)
        remove.color = (0.65, 0.18, 0.20, 1)
        remove.bind(on_release=lambda *_: self.delete_callback(self.item))
        title_row.add_widget(remove)
        self.add_widget(title_row)

        date_label = Label(
            text=f"{item.get('date', '')}  •  {item.get('time', '')}",
            size_hint_y=None,
            height=dp(25),
            color=(0.35, 0.20, 0.70, 1),
            font_size="14sp",
            halign="left",
            valign="middle",
            text_size=(0, None),
        )
        date_label.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        self.add_widget(date_label)

        if item.get("text"):
            body = Label(
                text=item.get("text", ""),
                color=(0.29, 0.27, 0.36, 1),
                font_size="15sp",
                halign="left",
                valign="top",
                text_size=(0, None),
            )
            body.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
            self.add_widget(body)


class RemindersScreen(Screen):
    STORAGE_DIR = "mobile_data"
    STORAGE_FILE = os.path.join(STORAGE_DIR, "personal_reminders.json")

    def on_pre_enter(self, *args):
        self.render_list()

    def get_user(self):
        return MDApp.get_running_app().current_user or {}

    def user_login(self):
        return (self.get_user().get("login") or "").strip()

    def ensure_storage(self):
        os.makedirs(self.STORAGE_DIR, exist_ok=True)
        if not os.path.exists(self.STORAGE_FILE):
            with open(self.STORAGE_FILE, "w", encoding="utf-8") as file:
                json.dump({}, file, ensure_ascii=False, indent=2)

    def load_all(self):
        self.ensure_storage()
        try:
            with open(self.STORAGE_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def save_all(self, data):
        self.ensure_storage()
        with open(self.STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def add_label(self, text, height, font_size, color, bold=False, halign="center"):
        label = Label(
            text=text,
            size_hint_y=None,
            height=dp(height),
            color=color,
            font_size=font_size,
            bold=bold,
            halign=halign,
            valign="middle",
            text_size=(0, None),
        )
        label.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        self.ids.content.add_widget(label)
        return label

    def clear_content(self):
        self.ids.content.clear_widgets()

    def render_list(self):
        self.clear_content()
        content = self.ids.content

        self.add_label("Напоминания", 54, "30sp", (0.10, 0.08, 0.16, 1), True)

        add_button = RoundedButton(text="Добавить 🔔", size_hint_y=None, height=dp(62), font_size="18sp", purple=True)
        add_button.bind(on_release=lambda *_: self.open_add_form())
        content.add_widget(add_button)

        now = datetime.now()
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

        date_card = WhiteCard(orientation="vertical", size_hint_y=None, height=dp(92), padding=(dp(15), dp(8)), spacing=0)
        day = Label(text=weekdays[now.weekday()], color=(0.10, 0.08, 0.16, 1), font_size="23sp", bold=True, halign="center", valign="middle", text_size=(0, None))
        day.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        date_card.add_widget(day)
        date_label = Label(text=f"{now.day} {months[now.month - 1]} {now.year} г.", color=(0.42, 0.40, 0.48, 1), font_size="15sp", halign="center", valign="middle", text_size=(0, None))
        date_label.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        date_card.add_widget(date_label)
        content.add_widget(date_card)

        items = self.get_user_reminders()
        if not items:
            empty = WhiteCard(orientation="vertical", size_hint_y=None, height=dp(112), padding=dp(14), spacing=dp(4))
            empty.add_widget(self.make_inner_label("Личных напоминаний пока нет", "18sp", True, (0.30, 0.28, 0.36, 1)))
            empty.add_widget(self.make_inner_label("Нажми «Добавить 🔔», чтобы создать первое", "14sp", False, (0.42, 0.40, 0.48, 1)))
            content.add_widget(empty)
            return

        self.add_label("Мои напоминания", 38, "23sp", (0.10, 0.08, 0.16, 1), True, "left")
        for item in items:
            content.add_widget(ReminderCard(item, self.delete_reminder))

    def make_inner_label(self, text, font_size, bold, color):
        label = Label(text=text, font_size=font_size, bold=bold, color=color, halign="center", valign="middle", text_size=(0, None))
        label.bind(width=lambda widget, value: setattr(widget, "text_size", (value, None)))
        return label

    def get_user_reminders(self):
        data = self.load_all()
        items = data.get(self.user_login(), [])
        if not isinstance(items, list):
            return []
        return sorted(items, key=lambda item: (item.get("date", ""), item.get("time", "")))

    def open_add_form(self):
        self.clear_content()
        content = self.ids.content
        self.add_label("Новое напоминание", 54, "29sp", (0.10, 0.08, 0.16, 1), True)

        form = WhiteCard(orientation="vertical", size_hint_y=None, height=dp(395), padding=dp(17), spacing=dp(11))
        self.date_input = Field(hint_text="Дата YYYY-MM-DD", text=datetime.now().strftime("%Y-%m-%d"), size_hint_y=None, height=dp(52))
        self.time_input = Field(hint_text="Время HH:MM", text=datetime.now().strftime("%H:%M"), size_hint_y=None, height=dp(52))
        self.title_input = Field(hint_text="Тема", size_hint_y=None, height=dp(52))
        self.text_input = Field(hint_text="Текст напоминания", multiline=True, size_hint_y=None, height=dp(100))
        for field in (self.date_input, self.time_input, self.title_input, self.text_input):
            form.add_widget(field)
        content.add_widget(form)

        save = RoundedButton(text="Сохранить", size_hint_y=None, height=dp(62), font_size="18sp", purple=True)
        save.bind(on_release=lambda *_: self.save_reminder())
        content.add_widget(save)

        cancel = RoundedButton(text="Отмена", size_hint_y=None, height=dp(50), font_size="16sp")
        cancel.bind(on_release=lambda *_: self.render_list())
        content.add_widget(cancel)

    def save_reminder(self):
        login = self.user_login()
        date_value = self.date_input.text.strip()
        time_value = self.time_input.text.strip()
        title_value = self.title_input.text.strip()
        text_value = self.text_input.text.strip()

        if not login:
            toast("Нет логина пользователя")
            return
        try:
            datetime.strptime(date_value, "%Y-%m-%d")
            datetime.strptime(time_value, "%H:%M")
        except ValueError:
            toast("Дата или время введены неверно")
            return
        if not title_value or not text_value:
            toast("Заполни тему и текст напоминания")
            return

        user = self.get_user()
        item = {
            "owner_login": login,
            "owner_fio": user.get("fio") or "",
            "date": date_value,
            "time": time_value,
            "title": title_value,
            "text": text_value,
        }

        data = self.load_all()
        data.setdefault(login, [])
        data[login].append(item)
        self.save_all(data)
        toast("Напоминание сохранено")
        self.render_list()

    def delete_reminder(self, reminder):
        login = self.user_login()
        data = self.load_all()
        data[login] = [item for item in data.get(login, []) if not self.same_item(item, reminder)]
        self.save_all(data)
        toast("Напоминание удалено")
        self.render_list()

    def same_item(self, first, second):
        return (
            first.get("date") == second.get("date")
            and first.get("time") == second.get("time")
            and first.get("title") == second.get("title")
            and first.get("text") == second.get("text")
            and (first.get("owner_login") or "") == (second.get("owner_login") or "")
        )

    def go_back(self):
        self.manager.current = "home"