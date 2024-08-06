from evdev import InputDevice, categorize, ecodes, list_devices

# 列出所有输入设备
devices = [InputDevice(path) for path in list_devices()]

# 打印所有设备以便调试
for device in devices:
    print(f"设备名: {device.name}, 设备路径: {device.path}")

# 找到鼠标设备
mouse_devices = []
for device in devices:
    capabilities = device.capabilities()
    if ecodes.EV_REL in capabilities and ecodes.EV_KEY in capabilities:
        if ecodes.REL_X in capabilities[ecodes.EV_REL] and ecodes.REL_Y in capabilities[ecodes.EV_REL]:
            if ecodes.BTN_LEFT in capabilities[ecodes.EV_KEY] or ecodes.BTN_RIGHT in capabilities[ecodes.EV_KEY]:
                mouse_devices.append(device)

if not mouse_devices:
    print("没有找到鼠标设备")
else:
    for mouse in mouse_devices:
        print(f"监听设备: {mouse.name} at {mouse.path}")
        try:
            for event in mouse.read_loop():
                if event.type == ecodes.EV_REL:
                    if event.code == ecodes.REL_X:
                        print(f"Mouse moved X: {event.value}")
                    elif event.code == ecodes.REL_Y:
                        print(f"Mouse moved Y: {event.value}")
                elif event.type == ecodes.EV_KEY:
                    if event.code == ecodes.BTN_LEFT:
                        if event.value == 1:
                            print("Left button pressed")
                        elif event.value == 0:
                            print("Left button released")
                    elif event.code == ecodes.BTN_RIGHT:
                        if event.value == 1:
                            print("Right button pressed")
                        elif event.value == 0:
                            print("Right button released")
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
