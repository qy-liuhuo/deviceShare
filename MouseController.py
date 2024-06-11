import pynput
import platform


class MouseController:
    def __init__(self):
        # 解决windows下缩放偏移问题
        if platform.system().lower() == 'windows':
            import ctypes
            awareness = ctypes.c_int()
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        self.__mouse = pynput.mouse.Controller()

    def get_position(self):
        return f"{self.__mouse.position[0]}, {self.__mouse.position[1]}"

    def move_to(self, position: tuple):
        self.__mouse.position = position

    def click(self, button, pressed):
        self.__mouse.click(button, pressed)

    def mouse_listener(self, on_click, on_move):
        return pynput.mouse.Listener(on_click=on_click, on_move=on_move)
