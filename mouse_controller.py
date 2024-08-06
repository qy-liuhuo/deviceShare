import threading
import time

from evdev import InputDevice, categorize, ecodes, list_devices, UInput
import subprocess


class MouseController:

    def __init__(self):
        devices = [InputDevice(path) for path in list_devices()]
        self.stop_event = threading.Event()
        self.mouse_devices = []
        for device in devices:
            capabilities = device.capabilities()
            if ecodes.EV_REL in capabilities and ecodes.EV_KEY in capabilities:
                if ecodes.REL_X in capabilities[ecodes.EV_REL] and ecodes.REL_Y in capabilities[ecodes.EV_REL]:
                    if ecodes.BTN_LEFT in capabilities[ecodes.EV_KEY] or ecodes.BTN_RIGHT in capabilities[
                        ecodes.EV_KEY]:
                        self.mouse_devices.append(device)
        capabilities = {ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y, ecodes.REL_WHEEL],
                        ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]}
        self.ui = UInput(capabilities, name="virtual_mouse")

    def update_last_position(self):
        pass

    def get_last_position(self):
        pass

    def get_position(self):
        result = subprocess.run(['xdotool', 'getmouselocation'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        output = result.stdout
        # 解析输出
        location = {}
        for item in output.split():
            key, value = item.split(':')
            location[key] = int(value)
        return location['x'], location['y']

    def move_to(self, position: tuple):
        pass

    def move(self, dx, dy):
        pass

    def scroll(self, dx, dy):
        pass

    def click(self, button, pressed):
        pass

    def run_mouse_listener(self, mouse, on_click, on_move, on_scroll, suppress=False):
        if suppress:
            mouse.grab()
        try:
            while not self.stop_event.is_set():
                event = mouse.read_one()  # 非阻塞读取事件
                if event:
                    if event.type == ecodes.EV_REL:
                        # if event.code == ecodes.REL_X:
                        #     on_move(event.value, 0)
                        # elif event.code == ecodes.REL_Y:
                        #     on_move(0, event.value)
                        # elif event.code == ecodes.REL_WHEEL:
                        #     on_scroll(0, event.value)
                        print(f"REL: {event}")
                    elif event.type == ecodes.EV_KEY:
                        if event.code == ecodes.BTN_LEFT:
                            if event.value == 1:
                                on_click('Button.left', 'press')
                            elif event.value == 0:
                                on_click('Button.left', 'release')
                        elif event.code == ecodes.BTN_RIGHT:
                            if event.value == 1:
                                on_click('Button.right', 'press')
                            elif event.value == 0:
                                on_click('Button.right', 'release')
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if suppress:
                mouse.ungrab()

    def mouse_listener(self, on_click, on_move, on_scroll, suppress=False):
        self.listener = []
        for mouse in self.mouse_devices:
            print(f"监听设备: {mouse.name} at {mouse.path}")
            self.listener.append(threading.Thread(target=self.run_mouse_listener,args=(mouse, on_click, on_move, on_scroll, suppress)))
        for i in self.listener:
            i.start()
        return self.listener

    def stop_listener(self):
        self.stop_event.set()
        self.listener.clear()

    def __del__(self):
        self.ui.close()


if __name__ == '__main__':

    mouseController = MouseController()
    mouseController.mouse_listener(None, None, None, suppress=True)
    for i in range(10):
        mouseController.click('Button.left', 'press')
        time.sleep(0.01)
        mouseController.click('Button.left', 'release')
        time.sleep(1)
    mouseController.stop_listener()