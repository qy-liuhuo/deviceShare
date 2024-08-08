from evdev import UInput, ecodes
import time


# 创建一个虚拟输入设备
capabilities = {ecodes.EV_KEY: [code for code in ecodes.ecodes if isinstance(code, int) and code >= ecodes.KEY_ESC and code <= ecodes.KEY_MAX]}
ui = UInput(capabilities, name="virtual_keyboard")

# 函数：模拟按键
def simulate_key_press(key_code):
    ui.write(ecodes.EV_KEY, key_code, 1)  # 按下按键
    ui.syn()
    time.sleep(0.1)  # 模拟按键按下的时间
    ui.write(ecodes.EV_KEY, key_code, 0)  # 松开按键
    ui.syn()

# 模拟输入 "HELLO"
keys = [ecodes.KEY_H, ecodes.KEY_E, ecodes.KEY_L, ecodes.KEY_L, ecodes.KEY_O]
for key in keys:
    simulate_key_press(key)
    time.sleep(0.2)  # 模拟每个按键之间的时间间隔

# 关闭虚拟设备
ui.close()