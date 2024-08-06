import platform
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

    def mouse_listener(self, on_click, on_move,on_scroll,suppress=False):
        import pynput
        return pynput.mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll,suppress=suppress)

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