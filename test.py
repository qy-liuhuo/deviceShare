from evdev import UInput, ecodes
import time

# 创建一个虚拟输入设备
capabilities = {
    ecodes.EV_KEY: [
        ecodes.KEY_A, ecodes.KEY_B, ecodes.KEY_C,
        ecodes.KEY_D, ecodes.KEY_E, ecodes.KEY_F,
        ecodes.KEY_G, ecodes.KEY_H, ecodes.KEY_I,
        ecodes.KEY_J, ecodes.KEY_K, ecodes.KEY_L,
        ecodes.KEY_M, ecodes.KEY_N, ecodes.KEY_O,
        ecodes.KEY_P, ecodes.KEY_Q, ecodes.KEY_R,
        ecodes.KEY_S, ecodes.KEY_T, ecodes.KEY_U,
        ecodes.KEY_V, ecodes.KEY_W, ecodes.KEY_X,
        ecodes.KEY_Y, ecodes.KEY_Z,
        ecodes.KEY_ENTER, ecodes.KEY_SPACE,
    ]
}

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
