import time

from evdev import InputDevice, categorize, ecodes, list_devices, UInput
import os

# 列出所有输入设备
# devices = [InputDevice(path) for path in list_devices()]
#
# # 打印所有设备以便调试
# for device in devices:
#     print(f"设备名: {device.name}, 设备路径: {device.path}")
#
# # 找到在线的键盘设备
# keyboard_devices = []
# for device in devices:
#     if not os.path.exists(device.path):
#         continue
#     capabilities = device.capabilities()
#     if ecodes.EV_KEY in capabilities and ecodes.EV_SYN in capabilities:
#         if ecodes.KEY_A in capabilities[ecodes.EV_KEY]:  # 检查是否有键盘按键
#             keyboard_devices.append(device)
#
# if not keyboard_devices:
#     print("没有找到在线的键盘设备")
# else:
#     # 创建一个虚拟输入设备
#
#     for keyboard in keyboard_devices:
#         print(f"监听设备: {keyboard.name} at {keyboard.path}")
#         keyboard.grab()
#         try:
#             for event in keyboard.read_loop():
#                 if event.type == ecodes.EV_KEY:
#                     # 处理事件，例如打印或修改事件
#                     print(f"事件: {event}")
#
#         except KeyboardInterrupt:
#             print("Stopped listening for events.")
#         except Exception as e:
#             print(f"发生错误: {e}")
#         finally:
#             keyboard.ungrab()
#     # 关闭虚拟设备
#     ui.close()

# capabilities = {ecodes.EV_KEY: list(ecodes.keys.keys())}
# ui = UInput(capabilities, name="virtual_keyboard")
# for i in range(10):
#     ui.write(ecodes.EV_KEY, ecodes.KEY_A, 1)
#     ui.syn()
#     time.sleep(1)
#     ui.write(ecodes.EV_KEY, ecodes.KEY_A, 0)
#     ui.syn()
#     time.sleep(2)
# ui.close()
from pynput import mouse

def on_move(x, y):
    print('Pointer0 moved to {0}'.format((x, y)))

# Collect events until released
with mouse.Listener(on_move=on_move) as listener:
    listener.join()

