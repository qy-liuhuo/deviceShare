"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
from pynput.keyboard import Key, KeyCode
from evdev import ecodes as e



class CodeConverter:
    """
    用于 pynput 的键码与evdev 的键码转换
    """
    def __init__(self):
        # 定义从 pynput 到 evdev 的键码映射
        self.pynput_to_evdev_dict = {
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
            Key.alt_r: e.KEY_RIGHTALT,
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
            Key.media_volume_down: e.KEY_VOLUMEDOWN,
            Key.media_volume_up: e.KEY_VOLUMEUP,
            Key.media_play_pause: e.KEY_PLAYPAUSE,
            Key.media_next: e.KEY_NEXTSONG,
            Key.media_previous: e.KEY_PREVIOUSSONG,
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
            '`': e.KEY_GRAVE,
            '-': e.KEY_MINUS,
            '=': e.KEY_EQUAL,
            '[': e.KEY_LEFTBRACE,
            ']': e.KEY_RIGHTBRACE,
            '\\': e.KEY_BACKSLASH,
            ';': e.KEY_SEMICOLON,
            '\'': e.KEY_APOSTROPHE,
            ',': e.KEY_COMMA,
            '.': e.KEY_DOT,
            '/': e.KEY_SLASH,
            '~': e.KEY_GRAVE,
            '_': e.KEY_MINUS,
            '+': e.KEY_EQUAL,
            '{': e.KEY_LEFTBRACE,
            '}': e.KEY_RIGHTBRACE,
            '|': e.KEY_BACKSLASH,
            ':': e.KEY_SEMICOLON,
            '"': e.KEY_APOSTROPHE,
            '<': e.KEY_COMMA,
            '>': e.KEY_DOT,
            '?': e.KEY_SLASH,

        }

        # 定义从 evdev 到 pynput 的键码映射
        self.evdev_to_pynput_dict = {int(v): k for k, v in self.pynput_to_evdev_dict.items()}
        

    def pynput_to_evdev_key(self,pynput_key):
        """
        将pynput的键码转换为evdev的键码
        :param pynput_key: pynput的键码
        :return: evdev的键码
        """
        return self.pynput_to_evdev_dict.get(pynput_key, None)

    def evdev_to_pynput_key(self,evdev_key):
        """
        将evdev的键码转换为pynput的键码
        :param evdev_key: evdev的键码
        :return: pynput的键码
        """
        return self.evdev_to_pynput_dict.get(evdev_key, None)



