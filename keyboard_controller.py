import threading
import time

from evdev import InputDevice, categorize, ecodes, list_devices, UInput
import os


class KeyboardController:
    def __init__(self):
        devices = [InputDevice(path) for path in list_devices()]
        # 打印所有设备以便调试
        # for device in devices:
        #     print(f"设备名: {device.name}, 设备路径: {device.path}")
        # 找到在线的键盘设备
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

    def press(self, key):
        self.ui.write(ecodes.EV_KEY, key, 1)
        self.ui.syn()

    def release(self, key):
        self.ui.write(ecodes.EV_KEY, ecodes.KEY_A, 0)
        self.ui.syn()

    def click(self, click_type, keyData):
        key = self.keyFactory.outPut(keyData)
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def run_keyboard_listener(self, keyboard, on_press, on_release, suppress=False):
        if suppress:
            print("lock")
            keyboard.grab()
        try:
            while not self.stop_event.is_set():
                event = keyboard.read_one()  # 非阻塞读取事件
                if event:
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        if key_event.keystate == key_event.key_down:
                            on_press(key_event.keycode)
                        elif key_event.keystate == key_event.key_up:
                            on_release(key_event.keycode)
                else:
                    time.sleep(0.01)  # 如果没有事件，休眠一段时间，减少 CPU 使用率
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if suppress:
                keyboard.ungrab()
        print("1234")

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


if __name__ == '__main__':
    def on_press(key):
        print(f"按下: {key}")

    def on_release(key):
        print(f"释放: {key}")

    keyboardController = KeyboardController()
    keyboardController.keyboard_listener(on_press, on_release, suppress=False)
    for i in range(10):
        keyboardController.press(ecodes.KEY_A)
        time.sleep(0.01)
        keyboardController.release(ecodes.KEY_A)
        time.sleep(1)
    keyboardController.stop_listener()
