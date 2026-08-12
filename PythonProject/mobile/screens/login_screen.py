from pathlib import Path

from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp

from mobile.services.api import login as api_login, ApiError


LOGO_PATH = (Path(__file__).resolve().parents[1] / "assets" / "school_logo.jpg").as_posix()

KV = '''
#:import dp kivy.metrics.dp

<RoundButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    font_size: "22sp"
    bold: True
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<LoginInput>:
    multiline: False
    font_size: "20sp"
    padding: dp(22), dp(15)
    foreground_color: 0.12, 0.10, 0.18, 1
    hint_text_color: 0.55, 0.52, 0.64, 1
    cursor_color: 0.42, 0.26, 0.82, 1
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
            rgba: 0.84, 0.81, 0.92, 1
        Line:
            width: 1.1
            rounded_rectangle: self.x, self.y, self.width, self.height, self.height / 2

<LoginScreen>:
    canvas.before:
        Color:
            rgba: 0.93, 0.90, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size

    AnchorLayout:
        anchor_x: "center"
        anchor_y: "center"

        BoxLayout:
            orientation: "vertical"
            size_hint: None, None
            width: min(root.width - dp(56), dp(440))
            height: dp(640)
            spacing: dp(16)

            AnchorLayout:
                size_hint_y: None
                height: dp(142)
                anchor_x: "center"
                anchor_y: "center"

                FloatLayout:
                    size_hint: None, None
                    size: dp(142), dp(142)
                
                    canvas.before:
                        StencilPush
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(28)]
                        StencilUse
                
                    canvas.after:
                        StencilUnUse
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [dp(28)]
                        StencilPop
                
                    Image:
                        source: root.logo_path
                        size_hint: 1, 1
                        allow_stretch: True
                        keep_ratio: False

            Label:
                size_hint_y: None
                height: dp(54)
                text: "Вход в приложение"
                font_size: "32sp"
                bold: True
                color: 0.42, 0.29, 0.86, 1
                halign: "center"
                valign: "middle"
                text_size: self.size

            Label:
                size_hint_y: None
                height: dp(34)
                text: "Гимназия Доброграда"
                font_size: "20sp"
                color: 0.30, 0.28, 0.36, 1
                halign: "center"
                valign: "middle"
                text_size: self.size

            Widget:
                size_hint_y: None
                height: dp(8)

            FloatLayout:
                size_hint_y: None
                height: dp(300)
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(30)]

                BoxLayout:
                    orientation: "vertical"
                    size_hint: 0.84, None
                    height: dp(210)
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    spacing: dp(16)

                    LoginInput:
                        id: login_input
                        hint_text: "Логин"
                        size_hint_y: None
                        height: dp(62)
                        on_text_validate: password_input.focus = True

                    LoginInput:
                        id: password_input
                        hint_text: "Пароль"
                        password: True
                        size_hint_y: None
                        height: dp(62)
                        on_text_validate: root.do_login()

                    RoundButton:
                        id: login_button
                        text: "Войти"
                        size_hint_y: None
                        height: dp(66)
                        bg_color: 0.42, 0.27, 0.84, 1
                        on_release: root.do_login()

            Label:
                id: message
                size_hint_y: None
                height: dp(30)
                text: ""
                font_size: "15sp"
                color: 0.82, 0.18, 0.25, 1
                halign: "center"
                valign: "middle"
                text_size: self.size
'''

Builder.load_string(KV)


class RoundButton(Button):
    bg_color = ListProperty([0.42, 0.27, 0.84, 1])


class LoginInput(TextInput):
    pass


class LoginScreen(Screen):
    logo_path = StringProperty(LOGO_PATH)

    def on_pre_enter(self, *args):
        self.ids.password_input.text = ""
        self.ids.message.text = ""
        self.ids.login_button.disabled = False
        self.ids.login_button.opacity = 1

    def show_error(self, text):
        self.ids.message.color = 0.82, 0.18, 0.25, 1
        self.ids.message.text = text

    def do_login(self):
        login_value = self.ids.login_input.text.strip()
        password_value = self.ids.password_input.text.strip()

        if not login_value or not password_value:
            self.show_error("Введите логин и пароль")
            return

        self.ids.message.color = 0.34, 0.20, 0.70, 1
        self.ids.message.text = "Проверяем данные..."
        self.ids.login_button.disabled = True
        self.ids.login_button.opacity = 0.65

        try:
            data = api_login(login_value, password_value)
        except ApiError as error:
            self.ids.login_button.disabled = False
            self.ids.login_button.opacity = 1
            self.show_error(str(error))
            return
        except Exception:
            self.ids.login_button.disabled = False
            self.ids.login_button.opacity = 1
            self.show_error("Не удалось выполнить вход")
            return

        user = {
            "login": data.get("login") or login_value,
            "fio": data.get("fio") or "",
            "role": data.get("role") or "",
            "klass": data.get("klass") or "",
            "profile": data.get("profile") or "",
            "subject": data.get("subject") or "",
            "cabinet": data.get("cabinet") or "",
            "admin": bool(data.get("admin", False)),
            "classroom": data.get("classroom") or "",
        }

        app = MDApp.get_running_app()
        app.set_current_user(user)
        self.ids.password_input.text = ""
        self.ids.login_button.disabled = False
        self.ids.login_button.opacity = 1
        self.manager.current = "home"