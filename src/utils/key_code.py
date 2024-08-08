import enum
import unicodedata
import six



class KeyCode(object):
    """
    A :class:`KeyCode` represents the description of a key code used by the
    operating system.
    """
    #: The names of attributes used as platform extensions.
    _PLATFORM_EXTENSIONS = []

    def __init__(self, vk=None, char=None, is_dead=False, **kwargs):
        self.vk = vk
        self.char = six.text_type(char) if char is not None else None
        self.is_dead = is_dead

        if self.is_dead:
            try:
                self.combining = unicodedata.lookup(
                    'COMBINING ' + unicodedata.name(self.char))
            except KeyError:
                self.is_dead = False
                self.combining = None
            if self.is_dead and not self.combining:
                raise KeyError(char)
        else:
            self.combining = None

        for key in self._PLATFORM_EXTENSIONS:
            setattr(self, key, kwargs.pop(key, None))
        if kwargs:
            raise ValueError(kwargs)


    def __repr__(self):
        if self.is_dead:
            return '[%s]' % repr(self.char)
        if self.char is not None:
            return repr(self.char)
        else:
            return '<%d>' % self.vk

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.char is not None and other.char is not None:
            return self.char == other.char and self.is_dead == other.is_dead
        else:
            return self.vk == other.vk and all(
                getattr(self, f) == getattr(other, f)
                for f in self._PLATFORM_EXTENSIONS)

    def __hash__(self):
        return hash(repr(self))

    def join(self, key):
        """Applies this dead key to another key and returns the result.

        Joining a dead key with space (``' '``) or itself yields the non-dead
        version of this key, if one exists; for example,
        ``KeyCode.from_dead('~').join(KeyCode.from_char(' '))`` equals
        ``KeyCode.from_char('~')`` and
        ``KeyCode.from_dead('~').join(KeyCode.from_dead('~'))``.

        :param KeyCode key: The key to join with this key.

        :return: a key code

        :raises ValueError: if the keys cannot be joined
        """
        # A non-dead key cannot be joined
        if not self.is_dead:
            raise ValueError(self)

        # Joining two of the same keycodes, or joining with space, yields the
        # non-dead version of the key
        if key.char == ' ' or self == key:
            return self.from_char(self.char)

        # Otherwise we combine the characters
        if key.char is not None:
            combined = unicodedata.normalize(
                'NFC',
                key.char + self.combining)
            if combined:
                return self.from_char(combined)

        raise ValueError(key)

    @classmethod
    def from_vk(cls, vk, **kwargs):
        """Creates a key from a virtual key code.

        :param vk: The virtual key code.

        :param kwargs: Any other parameters to pass.

        :return: a key code
        """
        return cls(vk=vk, **kwargs)

    @classmethod
    def from_char(cls, char, **kwargs):
        """Creates a key from a character.

        :param str char: The character.

        :return: a key code
        """
        return cls(char=char, **kwargs)

    @classmethod
    def from_dead(cls, char, **kwargs):
        """Creates a dead key.

        :param char: The dead key. This should be the unicode character
            representing the stand alone character, such as ``'~'`` for
            *COMBINING TILDE*.

        :return: a key code
        """
        return cls(char=char, is_dead=True, **kwargs)


class Key(enum.Enum):
    """A class representing various buttons that may not correspond to
    letters. This includes modifier keys and function keys.

    The actual values for these items differ between platforms. Some platforms
    may have additional buttons, but these are guaranteed to be present
    everywhere.
    """
    #: A generic Alt key. This is a modifier.
    alt = KeyCode.from_vk(0)

    #: The left Alt key. This is a modifier.
    alt_l = KeyCode.from_vk(0)

    #: The right Alt key. This is a modifier.
    alt_r = KeyCode.from_vk(0)

    #: The AltGr key. This is a modifier.
    alt_gr = KeyCode.from_vk(0)

    #: The Backspace key.
    backspace = KeyCode.from_vk(0)

    #: The CapsLock key.
    caps_lock = KeyCode.from_vk(0)

    #: A generic command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd = KeyCode.from_vk(0)

    #: The left command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_l = KeyCode.from_vk(0)

    #: The right command button. On *PC* platforms, this corresponds to the
    #: Super key or Windows key, and on *Mac* it corresponds to the Command
    #: key. This may be a modifier.
    cmd_r = KeyCode.from_vk(0)

    #: A generic Ctrl key. This is a modifier.
    ctrl = KeyCode.from_vk(0)

    #: The left Ctrl key. This is a modifier.
    ctrl_l = KeyCode.from_vk(0)

    #: The right Ctrl key. This is a modifier.
    ctrl_r = KeyCode.from_vk(0)

    #: The Delete key.
    delete = KeyCode.from_vk(0)

    #: A down arrow key.
    down = KeyCode.from_vk(0)

    #: The End key.
    end = KeyCode.from_vk(0)

    #: The Enter or Return key.
    enter = KeyCode.from_vk(0)

    #: The Esc key.
    esc = KeyCode.from_vk(0)

    #: The function keys. F1 to F20 are defined.
    f1 = KeyCode.from_vk(0)
    f2 = KeyCode.from_vk(0)
    f3 = KeyCode.from_vk(0)
    f4 = KeyCode.from_vk(0)
    f5 = KeyCode.from_vk(0)
    f6 = KeyCode.from_vk(0)
    f7 = KeyCode.from_vk(0)
    f8 = KeyCode.from_vk(0)
    f9 = KeyCode.from_vk(0)
    f10 = KeyCode.from_vk(0)
    f11 = KeyCode.from_vk(0)
    f12 = KeyCode.from_vk(0)
    f13 = KeyCode.from_vk(0)
    f14 = KeyCode.from_vk(0)
    f15 = KeyCode.from_vk(0)
    f16 = KeyCode.from_vk(0)
    f17 = KeyCode.from_vk(0)
    f18 = KeyCode.from_vk(0)
    f19 = KeyCode.from_vk(0)
    f20 = KeyCode.from_vk(0)

    #: The Home key.
    home = KeyCode.from_vk(0)

    #: A left arrow key.
    left = KeyCode.from_vk(0)

    #: The PageDown key.
    page_down = KeyCode.from_vk(0)

    #: The PageUp key.
    page_up = KeyCode.from_vk(0)

    #: A right arrow key.
    right = KeyCode.from_vk(0)

    #: A generic Shift key. This is a modifier.
    shift = KeyCode.from_vk(0)

    #: The left Shift key. This is a modifier.
    shift_l = KeyCode.from_vk(0)

    #: The right Shift key. This is a modifier.
    shift_r = KeyCode.from_vk(0)

    #: The Space key.
    space = KeyCode.from_vk(0)

    #: The Tab key.
    tab = KeyCode.from_vk(0)

    #: An up arrow key.
    up = KeyCode.from_vk(0)

    #: The play/pause toggle.
    media_play_pause = KeyCode.from_vk(0)

    #: The volume mute button.
    media_volume_mute = KeyCode.from_vk(0)

    #: The volume down button.
    media_volume_down = KeyCode.from_vk(0)

    #: The volume up button.
    media_volume_up = KeyCode.from_vk(0)

    #: The previous track button.
    media_previous = KeyCode.from_vk(0)

    #: The next track button.
    media_next = KeyCode.from_vk(0)

    #: The Insert key. This may be undefined for some platforms.
    insert = KeyCode.from_vk(0)

    #: The Menu key. This may be undefined for some platforms.
    menu = KeyCode.from_vk(0)

    #: The NumLock key. This may be undefined for some platforms.
    num_lock = KeyCode.from_vk(0)

    #: The Pause/Break key. This may be undefined for some platforms.
    pause = KeyCode.from_vk(0)

    #: The PrintScreen key. This may be undefined for some platforms.
    print_screen = KeyCode.from_vk(0)

    #: The ScrollLock key. This may be undefined for some platforms.
    scroll_lock = KeyCode.from_vk(0)


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

