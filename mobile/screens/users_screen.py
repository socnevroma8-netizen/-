from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


KV = """
<UsersScreen>:
    ScrollView:
        MDBoxLayout:
            id: content_box
            orientation: "vertical"
            adaptive_height: True
            padding: "16dp"
            spacing: "12dp"
"""
Builder.load_string(KV)


class UsersScreen(Screen):
    def on_pre_enter(self, *args):
        self.render()

    def render(self):
        box = self.ids.content_box
        box.clear_widgets()

        app = MDApp.get_running_app()
        user = app.current_user or {}
        role = user.get("role", "")
        admin = user.get("admin", False)

        box.add_widget(
            MDLabel(
                text="База пользователей",
                halign="center",
                bold=True,
                adaptive_height=True,
            )
        )

        if not (role == "student" and admin):
            box.add_widget(
                MDLabel(
                    text="Доступ только для администратора",
                    halign="center",
                    adaptive_height=True,
                )
            )
            box.add_widget(
                MDFlatButton(
                    text="Назад",
                    on_release=lambda x: self.go_home(),
                )
            )
            return

        box.add_widget(
            MDLabel(
                text="Основная роль: ученик или педагог",
                adaptive_height=True,
            )
        )
        box.add_widget(
            MDLabel(
                text="Админ — дополнительное право доступа",
                adaptive_height=True,
            )
        )

        box.add_widget(
            MDRaisedButton(
                text="Новый пользователь",
                pos_hint={"center_x": 0.5},
            )
        )

        box.add_widget(
            MDLabel(
                text="Лазутина Елизавета Сергеевна, логин: Lisa, 10Б, Инфотех",
                adaptive_height=True,
            )
        )
        box.add_widget(
            MDLabel(
                text="Филин Александр Сергеевич, роль: педагог, Информатика, каб. 211, кл. рук. 10Б",
                adaptive_height=True,
            )
        )

        box.add_widget(
            MDFlatButton(
                text="Импортировать users.xlsx сейчас",
                on_release=lambda x: None,
            )
        )
        box.add_widget(
            MDFlatButton(
                text="Назад",
                on_release=lambda x: self.go_home(),
            )
        )

    def go_home(self):
        self.manager.current = "home"