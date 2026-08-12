from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp

from mobile.screens.login_screen import LoginScreen
from mobile.screens.home_screen import HomeScreen
from mobile.screens.schedule_screen import ScheduleScreen
from mobile.screens.reminders_screen import RemindersScreen
from mobile.screens.teachers_screen import TeachersScreen
from mobile.screens.transfer_screen import TransferScreen
from mobile.screens.users_screen import UsersScreen
from mobile.screens.admin_screen import AdminScreen


class ScheduleApp(MDApp):
    PURPLE = (0.39, 0.20, 0.72, 1)
    PURPLE_DARK = (0.27, 0.12, 0.55, 1)
    LAVENDER = (0.93, 0.91, 1.0, 1)

    def build(self):
        self.title = "Гимназия Доброграда"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_palette = "DeepPurple"
        self.theme_cls.accent_hue = "A400"
        self.current_user = None

        sm = ScreenManager(transition=FadeTransition(duration=0.18))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ScheduleScreen(name="schedule"))
        sm.add_widget(RemindersScreen(name="reminders"))
        sm.add_widget(TeachersScreen(name="teachers"))
        sm.add_widget(TransferScreen(name="transfer"))
        sm.add_widget(UsersScreen(name="users"))
        sm.add_widget(AdminScreen(name="admin"))
        sm.current = "login"
        return sm

    def set_current_user(self, user_data):
        self.current_user = user_data or None

    def is_admin(self):
        return bool(self.current_user and self.current_user.get("admin"))

    def go_home(self):
        if self.root:
            self.root.current = "home"

    def logout(self):
        self.current_user = None
        if self.root:
            self.root.current = "login"


if __name__ == "__main__":
    ScheduleApp().run()
