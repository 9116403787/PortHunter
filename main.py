from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import random

# ---------- تم ----------
BG = (0, 0, 0, 1)
GREEN = (0, 1, 0.2, 1)
DIM_GREEN = (0, 0.5, 0.1, 1)
RED = (1, 0.1, 0.1, 1)

Window.clearcolor = BG

# ---------- ویجت پس‌زمینه با خطوط اسکن ----------
class MatrixBG(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chars = []
        with self.canvas:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        Clock.schedule_interval(self.animate, 0.1)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def animate(self, dt):
        # placeholder برای انیمیشن ماتریکس (می‌تونیم بعداً کامل کنیم)
        pass

# ---------- اسکن پورت ----------
def scan_port(host, port, timeout=0.6):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                return port
    except Exception:
        pass
    return None

# ---------- UI ----------
class PortHunterUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=8, **kwargs)

        # عنوان
        title = Label(
            text='[ PORTHUNTER ]',
            font_size='28sp',
            color=GREEN,
            bold=True,
            size_hint_y=0.12
        )
        self.add_widget(title)

        sub = Label(
            text='>> ethical port scanner v1.0 <<',
            font_size='12sp',
            color=DIM_GREEN,
            size_hint_y=0.06
        )
        self.add_widget(sub)

        # ورودی IP
        self.target = TextInput(
            hint_text='TARGET IP  (e.g. 192.168.1.1)',
            multiline=False,
            foreground_color=GREEN,
            background_color=(0.05, 0.05, 0.05, 1),
            cursor_color=GREEN,
            font_size='16sp',
            size_hint_y=0.1
        )
        self.add_widget(self.target)

        # دکمه
        self.btn = Button(
            text='[ INITIATE SCAN ]',
            background_color=(0, 0.3, 0.1, 1),
            color=GREEN,
            font_size='18sp',
            bold=True,
            size_hint_y=0.1
        )
        self.btn.bind(on_press=self.start_scan)
        self.add_widget(self.btn)

        # خروجی
        self.output = Label(
            text='> awaiting target...',
            color=GREEN,
            font_size='13sp',
            halign='left',
            valign='top',
            size_hint_y=None
        )
        self.output.bind(texture_size=self.output.setter('size'))
        scroll = ScrollView(size_hint_y=0.62)
        scroll.add_widget(self.output)
        self.add_widget(scroll)

        # انیمیشن تایپ
        self.typing_event = None

    def type_text(self, text, speed=0.02):
        if self.typing_event:
            self.typing_event.cancel()
        self.output.text = ''
        self._full_text = text
        self._idx = 0
        self.typing_event = Clock.schedule_interval(self._type_step, speed)

    def _type_step(self, dt):
        if self._idx < len(self._full_text):
            self.output.text += self._full_text[self._idx]
            self._idx += 1
        else:
            self.typing_event.cancel()
            self.typing_event = None

    def start_scan(self, instance):
        host = self.target.text.strip()
        if not host:
            self.type_text('> ERROR: no target specified\n')
            return
        self.type_text(f'> scanning {host} ...\n')
        threading.Thread(target=self._do_scan, args=(host,), daemon=True).start()

    def _do_scan(self, host):
        ports = [21,22,23,25,53,80,110,143,443,445,3306,3389,8080,8443,5900,6379]
        found = []
        with ThreadPoolExecutor(max_workers=30) as ex:
            for r in ex.map(lambda p: scan_port(host, p), ports):
                if r:
                    found.append(r)
        # ساخت متن نتیجه
        lines = [f'> scan complete for {host}\n']
        if found:
            lines.append('> OPEN PORTS:\n')
            for p in found:
                lines.append(f'  [ + ] {p}\n')
        else:
            lines.append('> no open ports found.\n')
        lines.append('\n> scan finished.')
        Clock.schedule_once(lambda dt: self.type_text(''.join(lines)), 0)

# ---------- اپ ----------
class PortHunterApp(App):
    def build(self):
        return PortHunterUI()

if __name__ == '__main__':
    PortHunterApp().run()
    