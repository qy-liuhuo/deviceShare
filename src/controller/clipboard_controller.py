"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import pyperclip
import subprocess
from src.utils.plantform import is_wayland

def get_clipboard_controller():
    """
    获取剪切板控制器
    :return:
    """
    if is_wayland():
        return ClipboardControllerWayland()
    else:
        return ClipboardController()

class ClipboardController:
    """
    剪切板控制器
    """
    def __init__(self):
        """
        初始化
        """
        self.last_clipboard_text = ''

    def copy(self, text):
        """
        复制
        :param text: 复制的文本
        :return:
        """
        pyperclip.copy(text)

    def paste(self):
        """
        粘贴
        :return:
        """
        return pyperclip.paste()

    def get_last_clipboard_text(self):
        """
        获取上一次剪切板内容
        :return:
        """
        return self.last_clipboard_text

    def update_last_clipboard_text(self,text):
        """
        更新上一次剪切板内容
        :param text: 内容
        :return:
        """
        self.last_clipboard_text = text


class ClipboardControllerWayland(ClipboardController):
    """
    Wayland剪切板控制器
    """
    def __init__(self):
        super().__init__()

    def copy(self, text):
        """
        复制
        :param text: 内容
        :return:
        """
        process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))

    def paste(self):
        """
        粘贴
        :return: 内容
        """
        process = subprocess.Popen(['wl-paste'], stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8').strip()
