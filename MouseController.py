import pynput


class MouseController:
    def __init__(self):
        self.__mouse = pynput.mouse.Controller()

    def get_position(self):
        return f"{self.__mouse.position[0]}, {self.__mouse.position[1]}"

    def move(self, position: tuple):
        self.__mouse.move(position[0], position[1])
        self.__mouse.position = position

    def click(self, button, pressed):
        self.__mouse.click(button, pressed)

    def mouse_listener(self, on_click):
        return pynput.mouse.Listener(on_click=on_click)