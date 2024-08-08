from pynput.keyboard import Key, KeyCode

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



