import pynput


class KeyboardController:
    def __init__(self):
        self.__keyboard = pynput.keyboard.Controller()

    def press(self, key):
        self.__keyboard.press(key)

    def release(self, key):
        self.__keyboard.release(key)

    def click(self, click_type, key_code):
        key = pynput.keyboard.KeyCode.from_vk(key_code)
        if click_type == 'press':
            self.press(key)
        elif click_type == 'release':
            self.release(key)

    def keyboard_listener(self, on_press, on_release):
        return pynput.keyboard.Listener(on_press=on_press, on_release=on_release)
