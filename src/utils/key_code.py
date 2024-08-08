from pynput.keyboard import Key, KeyCode
from evdev import ecodes as e
from pynput.keyboard import Key

# 创建 pynput 与 evdev 键码的映射字典
pynput_to_evdev = {
    Key.esc: e.KEY_ESC,
    Key.tab: e.KEY_TAB,
    Key.enter: e.KEY_ENTER,
    Key.space: e.KEY_SPACE,
    Key.backspace: e.KEY_BACKSPACE,
    Key.caps_lock: e.KEY_CAPSLOCK,
    Key.shift: e.KEY_LEFTSHIFT,
    Key.shift_r: e.KEY_RIGHTSHIFT,
    Key.ctrl: e.KEY_LEFTCTRL,
    Key.ctrl_r: e.KEY_RIGHTCTRL,
    Key.alt: e.KEY_LEFTALT,
    Key.alt_gr: e.KEY_RIGHTALT,
    Key.cmd: e.KEY_LEFTMETA,
    Key.cmd_r: e.KEY_RIGHTMETA,
    Key.up: e.KEY_UP,
    Key.down: e.KEY_DOWN,
    Key.left: e.KEY_LEFT,
    Key.right: e.KEY_RIGHT,
    Key.page_up: e.KEY_PAGEUP,
    Key.page_down: e.KEY_PAGEDOWN,
    Key.home: e.KEY_HOME,
    Key.end: e.KEY_END,
    Key.insert: e.KEY_INSERT,
    Key.delete: e.KEY_DELETE,
    Key.f1: e.KEY_F1,
    Key.f2: e.KEY_F2,
    Key.f3: e.KEY_F3,
    Key.f4: e.KEY_F4,
    Key.f5: e.KEY_F5,
    Key.f6: e.KEY_F6,
    Key.f7: e.KEY_F7,
    Key.f8: e.KEY_F8,
    Key.f9: e.KEY_F9,
    Key.f10: e.KEY_F10,
    Key.f11: e.KEY_F11,
    Key.f12: e.KEY_F12,
    Key.num_lock: e.KEY_NUMLOCK,
    Key.print_screen: e.KEY_SYSRQ,
    Key.scroll_lock: e.KEY_SCROLLLOCK,
    Key.pause: e.KEY_PAUSE,
    Key.menu: e.KEY_MENU,
    'a': e.KEY_A,
    'b': e.KEY_B,
    'c': e.KEY_C,
    'd': e.KEY_D,
    'e': e.KEY_E,
    'f': e.KEY_F,
    'g': e.KEY_G,
    'h': e.KEY_H,
    'i': e.KEY_I,
    'j': e.KEY_J,
    'k': e.KEY_K,
    'l': e.KEY_L,
    'm': e.KEY_M,
    'n': e.KEY_N,
    'o': e.KEY_O,
    'p': e.KEY_P,
    'q': e.KEY_Q,
    'r': e.KEY_R,
    's': e.KEY_S,
    't': e.KEY_T,
    'u': e.KEY_U,
    'v': e.KEY_V,
    'w': e.KEY_W,
    'x': e.KEY_X,
    'y': e.KEY_Y,
    'z': e.KEY_Z,
    '1': e.KEY_1,
    '2': e.KEY_2,
    '3': e.KEY_3,
    '4': e.KEY_4,
    '5': e.KEY_5,
    '6': e.KEY_6,
    '7': e.KEY_7,
    '8': e.KEY_8,
    '9': e.KEY_9,
    '0': e.KEY_0,
    Key.numpad0: e.KEY_KP0,
    Key.numpad1: e.KEY_KP1,
    Key.numpad2: e.KEY_KP2,
    Key.numpad3: e.KEY_KP3,
    Key.numpad4: e.KEY_KP4,
    Key.numpad5: e.KEY_KP5,
    Key.numpad6: e.KEY_KP6,
    Key.numpad7: e.KEY_KP7,
    Key.numpad8: e.KEY_KP8,
    Key.numpad9: e.KEY_KP9,
    Key.numpad_divide: e.KEY_KPSLASH,
    Key.numpad_multiply: e.KEY_KPASTERISK,
    Key.numpad_subtract: e.KEY_KPMINUS,
    Key.numpad_add: e.KEY_KPPLUS,
    Key.numpad_enter: e.KEY_KPENTER,
    Key.numpad_decimal: e.KEY_KPDOT,
}

# 将 pynput 键码转换为 evdev 键码的函数
def pynput_to_evdev_key(key):
    try:
        return pynput_to_evdev[key]
    except KeyError:
        return None

# 示例：转换 pynput 的 Key.space 到 evdev 的键码
key = Key.space
evdev_key = pynput_to_evdev_key(key)
print(f'pynput key {key} maps to evdev key {evdev_key}')

class CodeConverter:
    def __init__(self):
        from evdev import ecodes
        # 定义从 pynput 到 evdev 的键码映射
        self.pynput_to_evdev = {
            Key.esc: ecodes.KEY_ESC,
            Key.f1: ecodes.KEY_F1,
            Key.f2: ecodes.KEY_F2,
            Key.f3: ecodes.KEY_F3,
            Key.f4: ecodes.KEY_F4,
            Key.f5: ecodes.KEY_F5,
            Key.f6: ecodes.KEY_F6,
            Key.f7: ecodes.KEY_F7,
            Key.f8: ecodes.KEY_F8,
            Key.f9: ecodes.KEY_F9,
            Key.f10: ecodes.KEY_F10,
            Key.f11: ecodes.KEY_F11,
            Key.f12: ecodes.KEY_F12,
            Key.print_screen: ecodes.KEY_SYSRQ,
            Key.scroll_lock: ecodes.KEY_SCROLLLOCK,
            Key.pause: ecodes.KEY_PAUSE,
            Key.insert: ecodes.KEY_INSERT,
            Key.delete: ecodes.KEY_DELETE,
            Key.home: ecodes.KEY_HOME,
            Key.end: ecodes.KEY_END,
            Key.page_up: ecodes.KEY_PAGEUP,
            Key.page_down: ecodes.KEY_PAGEDOWN,
            Key.right: ecodes.KEY_RIGHT,
            Key.left: ecodes.KEY_LEFT,
            Key.down: ecodes.KEY_DOWN,
            Key.up: ecodes.KEY_UP,
            Key.caps_lock: ecodes.KEY_CAPSLOCK,
            Key.num_lock: ecodes.KEY_NUMLOCK,
            Key.scroll_lock: ecodes.KEY_SCROLLLOCK,
            Key.shift: ecodes.KEY_LEFTSHIFT,
            Key.shift_r: ecodes.KEY_RIGHTSHIFT,
            Key.ctrl_l: ecodes.KEY_LEFTCTRL,
            Key.ctrl_r: ecodes.KEY_RIGHTCTRL,
            Key.alt_l: ecodes.KEY_LEFTALT,
            Key.alt_r: ecodes.KEY_RIGHTALT,
            Key.cmd_l: ecodes.KEY_LEFTMETA,
            Key.cmd_r: ecodes.KEY_RIGHTMETA,
            Key.space: ecodes.KEY_SPACE,
            Key.enter: ecodes.KEY_ENTER,
            Key.backspace: ecodes.KEY_BACKSPACE,
            Key.tab: ecodes.KEY_TAB,
        }

        # 添加字母键的映射
        for i in range(ord('a'), ord('z') + 1):
            self.pynput_to_evdev[KeyCode.from_char(chr(i))] = getattr(ecodes, f'KEY_{chr(i).upper()}')
        # 添加数字键的映射
        for i in range(ord('0'), ord('9') + 1):
            self.pynput_to_evdev[KeyCode.from_char(chr(i))] = getattr(ecodes, f'KEY_{chr(i)}')

        # 添加常用标点符号的映射
        self.pynput_to_evdev.update({
            KeyCode.from_char('`'): ecodes.KEY_GRAVE,
            KeyCode.from_char('-'): ecodes.KEY_MINUS,
            KeyCode.from_char('='): ecodes.KEY_EQUAL,
            KeyCode.from_char('['): ecodes.KEY_LEFTBRACE,
            KeyCode.from_char(']'): ecodes.KEY_RIGHTBRACE,
            KeyCode.from_char('\\'): ecodes.KEY_BACKSLASH,
            KeyCode.from_char(';'): ecodes.KEY_SEMICOLON,
            KeyCode.from_char('\''): ecodes.KEY_APOSTROPHE,
            KeyCode.from_char(','): ecodes.KEY_COMMA,
            KeyCode.from_char('.'): ecodes.KEY_DOT,
            KeyCode.from_char('/'): ecodes.KEY_SLASH,
            KeyCode.from_char('~'): ecodes.KEY_GRAVE,
            KeyCode.from_char('_'): ecodes.KEY_MINUS,
            KeyCode.from_char('+'): ecodes.KEY_EQUAL,
            KeyCode.from_char('{'): ecodes.KEY_LEFTBRACE,
            KeyCode.from_char('}'): ecodes.KEY_RIGHTBRACE,
            KeyCode.from_char('|'): ecodes.KEY_BACKSLASH,
            KeyCode.from_char(':'): ecodes.KEY_SEMICOLON,
            KeyCode.from_char('"'): ecodes.KEY_APOSTROPHE,
            KeyCode.from_char('<'): ecodes.KEY_COMMA,
            KeyCode.from_char('>'): ecodes.KEY_DOT,
            KeyCode.from_char('?'): ecodes.KEY_SLASH,
        })

        # 定义从 evdev 到 pynput 的键码映射
        self.evdev_to_pynput = {v: k for k, v in self.pynput_to_evdev.items()}


# 示例转换函数
    def pynput_to_evdev_key(self,pynput_key):
        return self.pynput_to_evdev.get(pynput_key, None)

    def evdev_to_pynput_key(self,evdev_key):
        return self.evdev_to_pynput.get(evdev_key, None)



