import pynput
import threading
import os
from evdev import ecodes
import time
class KeyboardControllerWayland:
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
        print(keyData)
        print(self.keyFactory.outPut(keyData))
        print(self.codeConvert.pynput_to_evdev_key(self.keyFactory.outPut(keyData)))
        key = self.codeConvert.pynput_to_evdev_key(self.keyFactory.outPut(keyData))
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
                            on_press(self.codeConvert.evdev_to_pynput_key(key_event.keycode))
                        elif key_event.keystate == key_event.key_up:
                            on_release(self.codeConvert.evdev_to_pynput_key(key_event.keycode))
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


kc = KeyboardControllerWayland()

for i in range(10):
    kc.press(ecodes.KEY_0)
    kc.release(ecodes.KEY_0)
    time.sleep(2)