import platform
import threading
import time

import pynput
class MouseController:

    def __init__(self):
        
        # 解决windows下缩放偏移问题
        if platform.system().lower() == 'windows':
            import ctypes
            awareness = ctypes.c_int()
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        self.__mouse = pynput.mouse.Controller()
        self.last_position = self.__mouse.position
        self.focus = True


    def update_last_position(self):
        self.last_position = self.get_position()

    def get_last_position(self):
        return self.last_position

    def get_position(self):
        return self.__mouse.position

    def move_to(self, position: tuple):
        self.__mouse.position = position

    def move(self, dx, dy):
        self.__mouse.move(dx, dy)
        return self.__mouse.position

    def scroll(self, dx, dy):
        self.__mouse.scroll(dx, dy)

    def click(self, button, pressed):
        if pressed:
            self.__mouse.press(button)
        else:
            self.__mouse.release(button)

    def run_mouse_listener(self, mouse, on_click, on_move, on_scroll, suppress=False):
        from evdev import InputDevice, categorize, ecodes, list_devices, UInput
        if suppress:
            mouse.grab()
        try:
            while not self.stop_event.is_set():
                event = mouse.read_one()  # 非阻塞读取事件
                if event:
                    if event.type == ecodes.EV_REL:
                        if event.code == ecodes.REL_X:
                            if not on_move(event.value, 0):
                                self.stop_event.set()
                        elif event.code == ecodes.REL_Y:
                            if not on_move(0, event.value):
                                self.stop_event.set()
                        elif event.code == ecodes.REL_WHEEL:
                            on_scroll(0, 0, 0, event.value)
                    elif event.type == ecodes.EV_KEY:
                        if event.code == ecodes.BTN_LEFT:
                            if event.value == 1:
                                on_click(0,0,'Button.left', True)
                            elif event.value == 0:
                                on_click(0,0,'Button.left', False)
                        elif event.code == ecodes.BTN_RIGHT:
                            if event.value == 1:
                                on_click(0,0,'Button.right', True)
                            elif event.value == 0:
                                on_click(0,0,'Button.right', False)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if suppress:
                mouse.ungrab()

    def mouse_listener(self, on_click, on_move,on_scroll,suppress=False):
        self.pynput_listener = pynput.mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll,suppress=suppress)
        return self.pynput_listener

    def mouse_listener_linux(self, on_click, on_move, on_scroll, suppress=False):
        from evdev import InputDevice, categorize, ecodes, list_devices, UInput
        devices = [InputDevice(path) for path in list_devices()]
        print(devices)
        self.stop_event = threading.Event()
        self.mouse_devices = []
        for device in devices:
            capabilities = device.capabilities()
            if ecodes.EV_REL in capabilities and ecodes.EV_KEY in capabilities:
                if ecodes.REL_X in capabilities[ecodes.EV_REL] and ecodes.REL_Y in capabilities[ecodes.EV_REL]:
                    if ecodes.BTN_LEFT in capabilities[ecodes.EV_KEY] or ecodes.BTN_RIGHT in capabilities[
                        ecodes.EV_KEY]:
                        self.mouse_devices.append(device)
        self.listener = []
        for mouse in self.mouse_devices:
            print(f"监听设备: {mouse.name} at {mouse.path}")
            self.listener.append(threading.Thread(target=self.run_mouse_listener,
                                                  args=(mouse, on_click, on_move, on_scroll, suppress)))
        for i in self.listener:
            i.start()
        for i in self.listener:
            i.join()

    def stop_listener_linux(self):
        self.stop_event.set()
        self.listener.clear()


def get_click_button(btn: str):
    if btn == 'Button.left':
        return pynput.mouse.Button.left
    elif btn == 'Button.right':
        return pynput.mouse.Button.right
    elif btn == 'Button.middle':
        return pynput.mouse.Button.middle
    return pynput.mouse.Button.unknown

if __name__ == '__main__':
    from evdev import InputDevice, categorize, ecodes, list_devices
    # 列出所有输入设备
    devices = [InputDevice(path) for path in list_devices()]
    print(devices)