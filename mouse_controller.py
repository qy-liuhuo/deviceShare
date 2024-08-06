from evdev import InputDevice, categorize, ecodes, list_devices, UInput

class MouseController:

    def __init__(self):
        devices = [InputDevice(path) for path in list_devices()]
        self.mouse_devices = []
        for device in devices:
            capabilities = device.capabilities()
            if ecodes.EV_REL in capabilities and ecodes.EV_KEY in capabilities:
                if ecodes.REL_X in capabilities[ecodes.EV_REL] and ecodes.REL_Y in capabilities[ecodes.EV_REL]:
                    if ecodes.BTN_LEFT in capabilities[ecodes.EV_KEY] or ecodes.BTN_RIGHT in capabilities[ecodes.EV_KEY]:
                        self.mouse_devices.append(device)
        capabilities = {ecodes.EV_REL: [ecodes.REL_X, ecodes.REL_Y, ecodes.REL_WHEEL], ecodes.EV_KEY: [ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE]}
        self.ui = UInput(capabilities, name="virtual_mouse")

    def update_last_position(self):
        pass

    def get_last_position(self):
        pass

    def get_position(self):
        pass

    def move_to(self, position: tuple):
        pass

    def move(self, dx, dy):
        pass

    def scroll(self, dx, dy):
        pass

    def click(self, button, pressed):
        pass

    def mouse_listener(self, on_click, on_move,on_scroll,suppress=False):
        pass

    def __del__(self):
        self.ui.close()


if __name__ == '__main__':
    mouseController = MouseController()