import os

from evdev import UInput, ecodes, AbsInfo
import time

# 定义鼠标设备的能力
capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_LEFT,
        ecodes.BTN_RIGHT,
        ecodes.BTN_MIDDLE,
    ],
    ecodes.EV_ABS: [
        (ecodes.ABS_X, AbsInfo(value=0, min=0, max=1920, fuzz=0, flat=0, resolution=0)),
        (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=1080, fuzz=0, flat=0, resolution=0)),
    ],
    ecodes.EV_REL: [
        ecodes.REL_WHEEL,
    ],
}

# 创建虚拟鼠标设备
ui = UInput(capabilities, name="virtual_mouse")

# 函数：模拟鼠标绝对位置移动
def simulate_mouse_abs_move(x, y):
    ui.write(ecodes.EV_ABS, ecodes.ABS_X, x)
    ui.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
    ui.syn()

# 函数：模拟鼠标点击
def simulate_mouse_click(button):
    ui.write(ecodes.EV_KEY, button, 1)  # 按下按钮
    ui.syn()
    time.sleep(0.1)
    ui.write(ecodes.EV_KEY, button, 0)  # 松开按钮
    ui.syn()

# 函数：模拟鼠标滚轮
def simulate_mouse_wheel(direction):
    ui.write(ecodes.EV_REL, ecodes.REL_WHEEL, direction)
    ui.syn()
    time.sleep(0.1)



# 示例：模拟鼠标操作
try:
    # 绝对位置移动鼠标
    simulate_mouse_abs_move(1000, 500)
    time.sleep(1)

    # 左键点击
    simulate_mouse_click(ecodes.BTN_LEFT)
    time.sleep(1)

    # 右键点击
    simulate_mouse_click(ecodes.BTN_RIGHT)
    time.sleep(1)

    # 滚轮向上滚动
    simulate_mouse_wheel(1)
    time.sleep(1)

    # 滚轮向下滚动
    simulate_mouse_wheel(-1)
    time.sleep(1)

finally:
    # 关闭虚拟设备
    ui.close()

