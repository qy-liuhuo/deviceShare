from evdev import UInput, ecodes
import time

# 定义鼠标设备的能力
capabilities = {
    ecodes.EV_KEY: [
        ecodes.BTN_LEFT,
        ecodes.BTN_RIGHT,
        ecodes.BTN_MIDDLE,
    ],
    ecodes.EV_REL: [
        ecodes.REL_X,
        ecodes.REL_Y,
        ecodes.REL_WHEEL,
    ],
}

# 创建虚拟鼠标设备
ui = UInput(capabilities, name="virtual_mouse")

# 函数：模拟鼠标移动
def simulate_mouse_move(dx, dy):
    ui.write(ecodes.EV_REL, ecodes.REL_X, dx)
    ui.write(ecodes.EV_REL, ecodes.REL_Y, dy)
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
    # 移动鼠标 (相对坐标)
    simulate_mouse_move(100, 100)
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
