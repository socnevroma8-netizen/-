from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle, Line

ROUTES = {
    "1": ("50 мест", "Ковров", [("08:10", "Ул. Волго-Донская (конечная)"), ("08:15", "Дом культуры «Родина» (напротив мед. центра)"), ("08:20", "ВНИИ «Сигнал»"), ("08:25", "Первомайский"), ("08:40", "Гимназия")], "17:10"),
    "2": ("34 места", "Ковров", [("07:45", "ул. Клязьминская (у дома 6)"), ("07:50", "Худ. школа"), ("08:00", "Площадь Победы"), ("08:05", "ТЦ «Мандарин» (для педагогов)"), ("08:35", "Гимназия")], "17:10"),
    "3": ("50 мест", "Ковров", [("08:05", "Маяковского (вдоль бульвара им. А. В. Тменова)"), ("08:15", "ЦГБ (Магнит Косметик)"), ("08:35", "Гимназия")], "17:10"),
    "4": ("50 мест", "Ковров", [("08:00", "ТЦ «Треугольник» (ул. Строителей)"), ("08:05", "ТЦ «Русь»"), ("08:35", "Гимназия")], "17:10"),
    "5": ("50 мест", "Ковров", [("07:55", "Лесная (рынок «Крупянишник»)"), ("08:00", "Пушкина (напротив «Дикси», ул. Зои Космодемьянской)"), ("08:05", "Сударь"), ("08:35", "Гимназия")], "17:10"),
    "6": ("50 мест", "Мелехово", [("08:25", "Аптека"), ("08:30", "Дворец спорта"), ("08:40", "Гимназия")], "17:10"),
    "7": ("50 мест", "Мелехово", [("08:25", "Дворец спорта"), ("08:30", "Красная горка"), ("08:35", "6-й магазин"), ("08:40", "Гимназия")], "17:10"),
    "8": ("34 места", "Мелехово", [("08:35", "7-й микрорайон (вдоль дороги)"), ("08:45", "Гимназия")], "16:45"),
    "9": ("34 места", "Доброград", [("08:25", "Бульвар Дружбы"), ("08:40", "Гимназия")], "16:50"),
    "10": ("50 мест", "Ковров", [("08:05", "ул. Мичурина (школа-интернат)"), ("08:10", "ул. Кирова"), ("08:12", "ул. Комсомольская (Аскона)"), ("08:40", "Гимназия")], "17:10"),
    "11": ("34 места", "Ковров", [("07:50", "ТЦ «Мандарин»"), ("08:00", "Лесная (Крупянишник)"), ("08:05", "ТЦ «Русь»"), ("08:35", "Гимназия")], "17:10"),
    "12": ("34 места", "Ковров / Мелехово", [("08:00", "Ул. Туманова"), ("08:05", "ул. Кирова"), ("08:20", "Школа (Мелехово)"), ("08:35", "Гимназия")], "17:10"),
}

class GlowRouteButton(Button):
    selected = BooleanProperty(False)
    bg_color = ListProperty([1, 1, 1, 1])

class TransferScreen(Screen):
    selected_route = StringProperty("1")

    def on_kv_post(self, *_):
        self.build_routes()
        self.render()

    def build_routes(self):
        bar = self.ids.route_bar
        bar.clear_widgets()
        for i in range(1, 15):
            value = str(i)
            button = GlowRouteButton(text=value, selected=value == self.selected_route, size_hint=(None, None), size=(dp(46), dp(46)))
            button.bind(on_release=lambda _, value=value: self.choose(value))
            bar.add_widget(button)

    def choose(self, value):
        self.selected_route = value
        for button in self.ids.route_bar.children:
            button.selected = button.text == value
        self.render()

    def render(self):
        content = self.ids.content
        content.clear_widgets()
        if self.selected_route in ("13", "14"):
            content.add_widget(self.extra_card())
            return
        bus, direction, outbound, return_time = ROUTES[self.selected_route]
        content.add_widget(self.hero(bus, direction))
        content.add_widget(self.section("ТУДА", outbound, False))
        content.add_widget(self.section("ОБРАТНО", [(return_time, "Гимназия")], True))

    def hero(self, bus, direction):
        card = Panel(orientation="vertical", size_hint_y=None, padding=dp(18), spacing=dp(6))
        card.add_widget(self.txt("МАРШРУТ " + self.selected_route, "14sp", True, (0.45, 0.35, 0.95, 1), 26))
        card.add_widget(self.txt(direction, "28sp", True, (0.10, 0.08, 0.18, 1), 42))
        card.add_widget(self.txt("Автобус  •  " + bus, "16sp", True, (0.38, 0.35, 0.48, 1), 28))
        return card

    def section(self, title, rows, return_section):
        block = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        block.bind(minimum_height=block.setter("height"))
        block.add_widget(self.txt(title, "16sp", True, (0.32, 0.25, 0.72, 1), 28))
        card = Panel(orientation="vertical", size_hint_y=None, padding=0, spacing=0)
        card.bind(minimum_height=card.setter("height"))
        for index, (time, stop) in enumerate(rows):
            last = index == len(rows) - 1
            height = dp(62 if len(stop) < 46 else 88)
            row = BoxLayout(size_hint_y=None, height=height, padding=(dp(15), dp(9)), spacing=dp(10))
            with row.canvas.before:
                Color(*(0.88, 0.98, 0.94, 1) if return_section or last else (1, 1, 1, 1))
                rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(14)])
            row.bind(pos=lambda w, p, rr=rr: setattr(rr, "pos", p), size=lambda w, s, rr=rr: setattr(rr, "size", s))
            row.add_widget(self.txt(time, "17sp", True, (0.27, 0.22, 0.72, 1), height, dp(78)))
            row.add_widget(self.wrap(stop, "16sp", True, (0.10, 0.08, 0.17, 1), height))
            card.add_widget(row)
            if not last:
                divider = BoxLayout(size_hint_y=None, height=dp(1))
                with divider.canvas.before:
                    Color(0.89, 0.88, 0.93, 1)
                    Line(points=[0, 0, dp(500), 0], width=1)
                card.add_widget(divider)
        block.add_widget(card)
        return block

    def extra_card(self):
        card = Panel(orientation="vertical", size_hint_y=None, padding=dp(22), spacing=dp(12))
        card.add_widget(self.txt("ДОПОЛНИТЕЛЬНЫЙ ТРАНСФЕР", "15sp", True, (0.38, 0.28, 0.80, 1), 28))
        card.add_widget(self.txt("Отправление от гимназии", "23sp", True, (0.10, 0.08, 0.17, 1), 38))
        card.add_widget(self.txt("18:45", "34sp", True, (0.27, 0.22, 0.72, 1), 48))
        card.add_widget(self.wrap("Для тех, кто остаётся на дополнительных занятиях.\nМаршрут и остановки будут определены по потребностям.", "16sp", False, (0.42, 0.40, 0.50, 1), dp(82)))
        return card

    def txt(self, text, font_size, bold, color, height, width=None):
        label = Label(text=text, size_hint=(None if width else 1, None), width=width or 0, height=dp(height) if isinstance(height, int) else height, font_size=font_size, bold=bold, color=color, halign="left", valign="middle")
        label.text_size = (width, None) if width else (None, None)
        if not width:
            label.bind(width=lambda w, value: setattr(w, "text_size", (value, None)))
        return label

    def wrap(self, text, font_size, bold, color, height):
        label = self.txt(text, font_size, bold, color, height)
        label.text_size = (None, None)
        label.bind(width=lambda w, value: setattr(w, "text_size", (value, None)))
        return label

    def go_home(self):
        self.manager.current = "home"

class Panel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(minimum_height=self.sync_height)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(26)])
        self.bind(pos=self.sync_shape, size=self.sync_shape)
    def sync_height(self, _, value):
        if self.height < value:
            self.height = value
    def sync_shape(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size

KV = '''
#:import dp kivy.metrics.dp
<GlowRouteButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    color: (1, 1, 1, 1) if self.selected else (0.10, 0.08, 0.17, 1)
    font_size: "16sp"
    bold: True
    canvas.before:
        Color:
            rgba: (0.18, 0.14, 0.32, 1) if self.selected else (1, 1, 1, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15)]
        Color:
            rgba: (0.35, 0.25, 0.85, 1)
        Line:
            width: 1.1
            rounded_rectangle: self.x, self.y, self.width, self.height, dp(15)
<TransferScreen>:
    canvas.before:
        Color:
            rgba: 0.93, 0.90, 0.99, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        padding: dp(14), dp(10), dp(14), dp(10)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            Button:
                text: "← Назад"
                size_hint_x: None
                width: dp(106)
                background_normal: ""
                background_color: 1, 1, 1, 1
                color: 0.36, 0.22, 0.73, 1
                bold: True
                on_release: root.go_home()
            Widget:
        Label:
            text: "Трансферы"
            size_hint_y: None
            height: dp(44)
            font_size: "30sp"
            bold: True
            color: 0.10, 0.08, 0.17, 1
            halign: "center"
            text_size: self.size
        ScrollView:
            do_scroll_x: True
            do_scroll_y: False
            size_hint_y: None
            height: dp(56)
            bar_width: 0
            BoxLayout:
                id: route_bar
                size_hint: None, None
                width: self.minimum_width
                height: dp(48)
                spacing: dp(8)
                padding: dp(2), dp(1)
        ScrollView:
            do_scroll_x: False
            bar_width: dp(4)
            BoxLayout:
                id: content
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(14)
                padding: 0, dp(3), 0, dp(28)
'''

Builder.load_string(KV)
