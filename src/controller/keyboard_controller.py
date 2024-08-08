import sys
import threading
import os
import time
from pynput.keyboard import Key, KeyCode
from src.utils.plantform import is_wayland
keyChars = r"1!2@3#4$5%6^7&8*9(0)-_=+[{]}\|/?,<.>".strip()
_keyChars = {keyChars[i]: keyChars[i + 1] for i in range(0, len(keyChars), 2)}
def get_keyboard_controller():
    if is_wayland():
        return KeyboardControllerWayland()
    else:
        return KeyboardController()
class KeyFactory:
    keyChars = _keyChars
    keyNames = {'cmd': 'alt', 'alt_l': 'cmd'}

    def __init__(self):
        self.shiftRelease = True

    def input(self, key):
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
    def __init__(self):
        import pynput
        self.__keyboard = pynput.keyboard.Controller()
        self.keyFactory = KeyFactory()

    def press(self, key):
        self.__keyboard.press(key)

    def release(self, key):
        self.__keyboard.release(key)

    def click(self, click_type, keyData):
        key = self.keyFactory.outPut(keyData)
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def keyboard_listener(self, on_press, on_release):
        import pynput
        return pynput.keyboard.Listener(suppress=True,on_press=on_press, on_release=on_release)



class KeyboardControllerWayland(KeyboardController):
    def __init__(self):
        from src.utils.key_code import CodeConverter
        super().__init__()
        from evdev import InputDevice, ecodes, list_devices, UInput
        devices = [InputDevice(path) for path in list_devices()]
        self.stop_event = threading.Event()
        self.keyboard_devices = []
        for device in devices:
            if not os.path.exists(device.path):
                continue
            capabilities = device.capabilities()
            if ecodes.EV_KEY in capabilities and ecodes.EV_SYN in capabilities:
                if ecodes.KEY_A in capabilities[ecodes.EV_KEY]:  # 检查是否有键盘按键
                    self.keyboard_devices.append(device)
        capabilities = {ecodes.EV_KEY: list(ecodes.keys.keys())}
        self.ui = UInput(capabilities, name="virtual_keyboard")
        self.codeConvert = CodeConverter()

    def press(self, key):
        from evdev import ecodes
        self.ui.write(ecodes.EV_KEY, key, 1)
        self.ui.syn()

    def release(self, key):
        from evdev import ecodes
        self.ui.write(ecodes.EV_KEY, key, 0)
        self.ui.syn()

    def click(self, click_type, keyData):
        key = self.codeConvert.pynput_to_evdev(self.keyFactory.outPut(keyData))
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def run_keyboard_listener(self, keyboard, on_press, on_release, suppress=False):
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
                            on_press(self.codeConvert.evdev_to_pynput(key_event.keycode))
                        elif key_event.keystate == key_event.key_up:
                            on_release(self.codeConvert.evdev_to_pynput(key_event.keycode))
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
        self.listener = []
        for keyboard in self.keyboard_devices:
            print(f"监听设备: {keyboard.name} at {keyboard.path}")
            self.listener.append(
                threading.Thread(target=self.run_keyboard_listener, args=(keyboard, on_press, on_release, suppress)))
        for i in self.listener:
            i.start()
        return self.listener

    def stop_listener(self):
        self.stop_event.set()
        self.listener.clear()

    def __del__(self):
        self.ui.close()