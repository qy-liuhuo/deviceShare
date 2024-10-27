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
import sys
import threading
import os
import time
from pynput.keyboard import Key, KeyCode
from src.utils.plantform import is_wayland

keyChars = r"1!2@3#4$5%6^7&8*9(0)-_=+[{]}\|/?,<.>".strip()
_keyChars = {keyChars[i]: keyChars[i + 1] for i in range(0, len(keyChars), 2)}


def get_keyboard_controller():
    """
    获取键盘控制器
    :return:
    """
    if is_wayland():
        return KeyboardControllerWayland()
    else:
        return KeyboardController()


class KeyFactory:
    """
    pynput键盘编码
    """
    keyChars = _keyChars
    keyNames = {'cmd': 'alt', 'alt_l': 'cmd'}

    def __init__(self):
        self.shiftRelease = True 

    def input(self, key):
        """
        输入
        :param key: 键
        :return: 编码结果
        """
        if isinstance(key,str):
            key = KeyCode.from_char(key)
        if 'name' in dir(key):
            if 'shift' in key.name:
                self.shiftRelease = not self.shiftRelease
            data = ("name", key.name)
        elif 'char' in dir(key) and key.char is not None:
            keyChar = key.char
            if not self.shiftRelease:
                keyChar = self.keyChars.get(keyChar, keyChar)
            data = ("char", keyChar)
        else:
            data = ("vk", key.vk)
        return data

    def outPut(self, data):
        """
        输出
        :param data: 编码
        :return: 键
        """
        tp, dt = data
        if tp == "name":
            if sys.platform == 'darwin':
                name = self.keyNames.get(dt, dt)
            else:
                name = dt
            try:
                key = Key[name]
            except:
                key = None
        elif tp == 'char':
            key = dt
        elif tp == 'vk':
            key = KeyCode.from_vk(dt)
        else:
            raise TypeError(str(data))
        return key


class KeyboardController:
    """
    pynput键盘控制器
    """
    def __init__(self):
        """
        初始化
        """
        import pynput
        self.__keyboard = pynput.keyboard.Controller()
        self.keyFactory = KeyFactory()

    def press(self, key):
        """
        按下
        :param key: 键
        :return:
        """
        self.__keyboard.press(key)

    def release(self, key):
        """
        释放
        :param key: 键
        :return:
        """
        self.__keyboard.release(key)

    def click(self, click_type, keyData):
        """
        点击
        :param click_type: 类型
        :param keyData: 键
        :return:
        """
        key = self.keyFactory.outPut(keyData)
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def keyboard_listener(self, on_press, on_release):
        """
        键盘监听
        :param on_press: 按下回调
        :param on_release: 释放回调
        :return:
        """
        import pynput
        return pynput.keyboard.Listener(suppress=True, on_press=on_press, on_release=on_release)


class KeyboardControllerWayland(KeyboardController):
    """
    Wayland键盘控制器
    """
    def __init__(self):
        """
        初始化
        """
        from src.utils.key_code import CodeConverter
        super().__init__()
        from evdev import InputDevice, ecodes, list_devices, UInput
        devices = [InputDevice(path) for path in list_devices()]
        self.stop_event = threading.Event()
        self.keyboard_devices = [] # 键盘设备
        for device in devices:
            if not os.path.exists(device.path):
                continue
            capabilities = device.capabilities()
            if ecodes.EV_KEY in capabilities and ecodes.EV_SYN in capabilities:
                if ecodes.KEY_A in capabilities[ecodes.EV_KEY]:  # 检查是否有键盘按键
                    self.keyboard_devices.append(device)
        self.codeConvert = CodeConverter()
        capabilities = { ecodes.EV_KEY: [code for code in self.codeConvert.pynput_to_evdev_dict.values()]} # 键盘能力
        self.ui = UInput(capabilities, name="virtual_keyboard") # 创建虚拟键盘
        

    def press(self, key):
        """
        按下
        :param key:  evdev键
        :return:
        """
        from evdev import ecodes
        self.ui.write(ecodes.EV_KEY, key, 1)
        self.ui.syn()

    def release(self, key):
        """
        释放
        :param key: evdev键
        :return:
        """
        from evdev import ecodes
        self.ui.write(ecodes.EV_KEY, key, 0)
        self.ui.syn()

    def click(self, click_type, keyData):
        """
        点击
        :param click_type: 类型
        :param keyData: 键
        :return:
        """
        key = self.codeConvert.pynput_to_evdev_key(self.keyFactory.outPut(keyData))
        if key is None:
            return
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def run_keyboard_listener(self, keyboard, on_press, on_release, suppress=False):
        """
        运行键盘监听
        :param keyboard: 键盘
        :param on_press:  按下回调
        :param on_release:  释放回调
        :param suppress:   是否抑制输出
        :return:
        """
        from evdev import ecodes, categorize
        if suppress:
            keyboard.grab()
        try:
            while not self.stop_event.is_set():
                event = keyboard.read_one()  # 非阻塞读取事件
                if event:
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        if key_event.keystate == key_event.key_down:
                            on_press(self.codeConvert.evdev_to_pynput_key(key_event.scancode))
                        elif key_event.keystate == key_event.key_up:
                            on_release(self.codeConvert.evdev_to_pynput_key(key_event.scancode))
                else:
                    time.sleep(0.01)  # 如果没有事件，休眠一段时间，减少 CPU 使用率
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if suppress:
                keyboard.ungrab()

    def keyboard_listener(self, on_press, on_release, suppress=False):
        """
        键盘监听
        :param on_press: 按下回调
        :param on_release: 释放回调
        :param suppress: 是否抑制输出
        :return:
        """
        self.stop_event.clear()
        self.listener = []
        for keyboard in self.keyboard_devices:
            print(f"监听设备: {keyboard.name} at {keyboard.path}")
            self.listener.append(
                threading.Thread(target=self.run_keyboard_listener, args=(keyboard, on_press, on_release, suppress)))
        for i in self.listener:
            i.start()
        return self.listener

    def stop_listener(self):
        """
        停止监听
        :return:
        """
        self.stop_event.set()
        self.listener.clear()

    def __del__(self):
        """
        析构,关闭虚拟键盘
        :return:
        """
        try:
            self.ui.close()
        except:
            pass
    