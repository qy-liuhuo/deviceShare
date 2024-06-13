import time

import pyperclip


class Content:
    def __init__(self, text, from_other=False):
        self.text = text
        self.from_other = from_other


class ClipBoardController:

    def __init__(self):
        self.clipboard = pyperclip
        self.content = None

    def paste(self):
        return self.clipboard.paste()

    def copy(self,text):
        return self.clipboard.copy(text)

    def get_content(self):
        return Content(self.clipboard.paste(), False)

    def set_content(self, content: Content):
        self.content = content
        self.clipboard.copy(content.text)

