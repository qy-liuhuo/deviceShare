from pynput.keyboard import Key, KeyCode

# 建立键码映射字典
keycode_mapping = {
    # 字母键
    KeyCode(char='a'): 30,
    KeyCode(char='b'): 48,
    KeyCode(char='c'): 46,
    KeyCode(char='d'): 32,
    KeyCode(char='e'): 18,
    KeyCode(char='f'): 33,
    KeyCode(char='g'): 34,
    KeyCode(char='h'): 35,
    KeyCode(char='i'): 23,
    KeyCode(char='j'): 36,
    KeyCode(char='k'): 37,
    KeyCode(char='l'): 38,
    KeyCode(char='m'): 50,
    KeyCode(char='n'): 49,
    KeyCode(char='o'): 24,
    KeyCode(char='p'): 25,
    KeyCode(char='q'): 16,
    KeyCode(char='r'): 19,
    KeyCode(char='s'): 31,
    KeyCode(char='t'): 20,
    KeyCode(char='u'): 22,
    KeyCode(char='v'): 47,
    KeyCode(char='w'): 17,
    KeyCode(char='x'): 45,
    KeyCode(char='y'): 21,
    KeyCode(char='z'): 44,

    # 数字键
    KeyCode(char='0'): 11,
    KeyCode(char='1'): 2,
    KeyCode(char='2'): 3,
    KeyCode(char='3'): 4,
    KeyCode(char='4'): 5,
    KeyCode(char='5'): 6,
    KeyCode(char='6'): 7,
    KeyCode(char='7'): 8,
    KeyCode(char='8'): 9,
    KeyCode(char='9'): 10,

    # 功能键
    Key.f1: 59,
    Key.f2: 60,
    Key.f3: 61,
    Key.f4: 62,
    Key.f5: 63,
    Key.f6: 64,
    Key.f7: 65,
    Key.f8: 66,
    Key.f9: 67,
    Key.f10: 68,
    Key.f11: 87,
    Key.f12: 88,

    # 控制键
    Key.enter: 28,
    Key.space: 57,
    Key.backspace: 14,
    Key.tab: 15,
    Key.esc: 1,

    # 箭头键
    Key.up: 103,
    Key.down: 108,
    Key.left: 105,
    Key.right: 106,

    # 修饰键
    Key.ctrl_l: 29,
    Key.ctrl_r: 97,
    Key.alt_l: 56,
    Key.alt_r: 100,
    Key.shift_l: 42,
    Key.shift_r: 54,
    Key.caps_lock: 58,

    # 特殊键
    Key.insert: 110,
    Key.delete: 111,
    Key.home: 102,
    Key.end: 107,
    Key.page_up: 104,
    Key.page_down: 109,
}

# 示例：获取某个键的键码
example_key = Key.enter
print(f"The keycode for {example_key} is {keycode_mapping.get(example_key)}")
