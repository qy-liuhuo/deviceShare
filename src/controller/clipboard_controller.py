import pyperclip
import subprocess
from src.utils.plantform import is_wayland

def get_clipboard_controller():
    if is_wayland():
        return ClipboardControllerWayland()
    else:
        return ClipboardController()

class ClipboardController:
    def __init__(self):
        self.last_clipboard_text = ''

    def copy(self, text):
        pyperclip.copy(text)

    def paste(self):
        return pyperclip.paste()

    def get_last_clipboard_text(self):
        return self.last_clipboard_text

    def update_last_clipboard_text(self,text):
        self.last_clipboard_text = text


class ClipboardControllerWayland(ClipboardController):
    def __init__(self):
        super().__init__()

    def copy(self, text):
        process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))

    def paste(self):
        process = subprocess.Popen(['wl-paste'], stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8')
