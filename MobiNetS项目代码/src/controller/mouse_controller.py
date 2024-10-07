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
import platform
import threading
import time
from screeninfo import get_monitors

from src.utils.plantform import is_wayland


class MouseController:
    """
    鼠标控制器
    """
    def __init__(self):
        # 解决windows下缩放偏移问题
        if platform.system().lower() == 'windows':
            import ctypes
            awareness = ctypes.c_int()
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if not is_wayland():
            import pynput
            self.__mouse = pynput.mouse.Controller()
            self.last_position = self.__mouse.position
        self.focus = True
        self.ui = None
        if is_wayland():
            # 创建虚拟鼠标设备
            from evdev import UInput, AbsInfo ,InputDevice, categorize, ecodes, list_devices
            monitors = get_monitors()
            # 定义鼠标设备的能力
            self.capabilities = {
                ecodes.EV_KEY: [
                    ecodes.BTN_LEFT,
                    ecodes.BTN_RIGHT,
                    ecodes.BTN_MIDDLE,
                ],
                ecodes.EV_ABS: [
                    (ecodes.ABS_X, AbsInfo(value=0, min=0, max=monitors[0].width, fuzz=0, flat=0, resolution=0)),
                    (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=monitors[0].height, fuzz=0, flat=0, resolution=0)),
                ],
                ecodes.EV_REL: [
                    ecodes.REL_X,
                    ecodes.REL_Y,
                    ecodes.REL_WHEEL,
                ],
            }

            # 创建虚拟鼠标设备
            self.ui = UInput(self.capabilities, name="virtual_mouse")
            self.position = (0,0)
        self.position = None

    def get_mouse_devices(self):
        """
        获取鼠标设备
        :return:
        """
        from evdev import InputDevice, ecodes, list_devices
        devices = [InputDevice(path) for path in list_devices()]
        mouse_devices = []
        for device in devices:
            capabilities = device.capabilities()
            if ecodes.EV_REL in capabilities and ecodes.EV_KEY in capabilities and "virtual" not in device.name:
                if ecodes.REL_X in capabilities[ecodes.EV_REL] and ecodes.REL_Y in capabilities[ecodes.EV_REL]:
                    if ecodes.BTN_LEFT in capabilities[ecodes.EV_KEY] or ecodes.BTN_RIGHT in capabilities[
                        ecodes.EV_KEY]:
                        mouse_devices.append(device)
        return mouse_devices 

    def update_last_position(self):
        """
        更新上一次位置
        :return:
        """
        self.last_position = self.get_position()

    def get_last_position(self):
        """
        获取上一次位置
        :return:
        """
        return self.last_position

    def get_position(self):
        """
        获取位置
        :return:
        """
        return self.__mouse.position

    def move_to(self, position: tuple):
        """
        移动到
        :param position: 绝对位置
        :return:
        """
        if is_wayland(): # wayland单独处理
            from evdev import ecodes
            self.ui.write(ecodes.EV_ABS, ecodes.ABS_X, position[0])
            self.ui.write(ecodes.EV_ABS, ecodes.ABS_Y, position[1])
            self.ui.syn()
            self.position = position
        else:
            self.__mouse.position = position

    def move(self, dx, dy):
        """
        移动
        :param dx: 位移
        :param dy: 位移
        :return:
        """
        if is_wayland(): # wayland单独处理
            from evdev import ecodes
            self.ui.write(ecodes.EV_REL, ecodes.REL_X, dx)
            self.ui.write(ecodes.EV_REL, ecodes.REL_Y, dy)
            self.position = (self.position[0] + dx, self.position[1] + dy)
            return self.position 
        else:
            self.__mouse.move(dx, dy)
            return self.__mouse.position

    def scroll(self, dx, dy):
        """
        滚动
        :param dx: 滚动位移x
        :param dy: 滚动位移y
        :return:
        """
        if is_wayland():
            from evdev import ecodes
            self.ui.write(ecodes.EV_REL, ecodes.REL_WHEEL, dy)
        else:
            self.__mouse.scroll(dx, dy)


    def click(self, button, pressed):
        """
        点击
        :param button: 按键
        :param pressed: 是否按下
        :return:
        """
        if is_wayland(): # wayland单独处理
            from evdev import ecodes
            def get_evdev_button(button):
                if button == 'Button.left':
                    return ecodes.BTN_LEFT
                elif button == 'Button.right':
                    return ecodes.BTN_RIGHT
                elif button == 'Button.middle':
                    return ecodes.BTN_MIDDLE
                return ecodes.BTN_LEFT

            if pressed:
                self.ui.write(ecodes.EV_KEY, get_evdev_button(button), 1)
            else:
                self.ui.write(ecodes.EV_KEY, get_evdev_button(button), 0)
            self.ui.syn()
        else:
            if pressed:
                self.__mouse.press(get_click_button(button))
            else:
                self.__mouse.release(get_click_button(button))

    def run_mouse_listener(self, mouse, on_click, on_move, on_scroll, suppress=False):
        """
        运行鼠标监听
        :param mouse:
        :param on_click:
        :param on_move:
        :param on_scroll:
        :param suppress:
        :return:
        """
        from evdev import InputDevice, categorize, ecodes, list_devices, UInput
        try:
            if suppress:
                mouse.grab()
            while not self.stop_event.is_set():
                event = mouse.read_one()  # 非阻塞读取事件
                if event:
                    if event.type == ecodes.EV_REL:
                        if event.code == ecodes.REL_X:
                            if not on_move(event.value, 0):
                                self.stop_event.set()
                        elif event.code == ecodes.REL_Y:
                            if not on_move(0, event.value):
                                self.stop_event.set()
                        elif event.code == ecodes.REL_WHEEL:
                            on_scroll(0, 0, 0, event.value)
                    elif event.type == ecodes.EV_KEY:
                        if event.code == ecodes.BTN_LEFT:
                            if event.value == 1:
                                on_click(0,0,'Button.left', True)
                            elif event.value == 0:
                                on_click(0,0,'Button.left', False)
                        elif event.code == ecodes.BTN_RIGHT:
                            if event.value == 1:
                                on_click(0,0,'Button.right', True)
                            elif event.value == 0:
                                on_click(0,0,'Button.right', False)
                else:
                    time.sleep(0.01)
        except KeyboardInterrupt:
            print("Stopped listening for events.")
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            if suppress:
                mouse.ungrab()

    def mouse_listener(self, on_click, on_move,on_scroll,suppress=False):
        """
        鼠标监听
        :param on_click:
        :param on_move:
        :param on_scroll:
        :param suppress:
        :return:
        """
        import pynput
        self.pynput_listener = pynput.mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll,suppress=suppress)
        return self.pynput_listener

    def update_position_by_listeners(self):
        """
        通过监听器更新位置
        :return:
        """
        from evdev import ecodes
        monitor = get_monitors()[0]
        self.stop_event_put = threading.Event()
        def on_move(mouse):
            if self.position is None:
                self.move_to((monitor.width // 2, monitor.height // 2))  # 同时也更新了self.position
            try:
                # mouse.grab()
                while not self.stop_event_put.is_set():
                    dx = 0
                    dy = 0
                    for i in range(100):
                        event = mouse.read_one()
                        if event:
                            if event.type == ecodes.EV_REL:
                                if event.code == ecodes.REL_X:
                                    # self.ui.write(ecodes.EV_REL, ecodes.REL_X, event.value)
                                    dx += event.value
                                elif event.code == ecodes.REL_Y:
                                    dy += event.value
                                    # self.ui.write(ecodes.EV_REL, ecodes.REL_Y, event.value)
                            # else:
                            #     self.ui.write(event.type , event.code, event.value)
                    old_x = self.position[0]
                    old_y = self.position[1]
                    new_x = old_x + dx
                    if new_x < 0:
                        new_x = 0
                    elif new_x > monitor.width:
                        new_x = monitor.width
                    new_y = old_y + dy
                    if new_y < 0:
                        new_y = 0
                    elif new_y > monitor.height:
                        new_y = monitor.height
                    self.position = (new_x,new_y)
            except Exception as e:
                print(e)
            finally:
                # mouse.ungrab()
                pass
        self.event_puter = []
        for mouse in self.get_mouse_devices():
            self.event_puter.append(threading.Thread(target=on_move,
                                                  args=(mouse,)))
        for i in self.event_puter:
            i.start()

    def wait_for_event_puter_stop(self):
        """
        等待事件监听停止
        :return:
        """
        self.stop_event_put.set()
        for i in self.event_puter:
            i.join()


    def mouse_listener_linux(self, on_click, on_move, on_scroll, suppress=False):
        """
        linux鼠标监听
        :param on_click:
        :param on_move:
        :param on_scroll:
        :param suppress:
        :return:
        """
        self.stop_event = threading.Event()
        self.listener = []
        for mouse in self.get_mouse_devices():
            # print(f"监听设备: {mouse.name} at {mouse.path}")
            self.listener.append(threading.Thread(target=self.run_mouse_listener,
                                                  args=(mouse, on_click, on_move, on_scroll, suppress)))
        for i in self.listener:
            i.start()
        monitor = get_monitors()[0]
        self.move_to((monitor.width // 2, monitor.height // 2))
        for i in self.listener:
            i.join()

    def stop_listener_linux(self):
        """
        停止监听
        :return:
        """
        self.stop_event.set()
        self.listener.clear()


def get_click_button(btn: str):
    """
    获取点击按钮
    :param btn:
    :return:
    """
    import pynput
    if btn == 'Button.left':
        return pynput.mouse.Button.left
    elif btn == 'Button.right':
        return pynput.mouse.Button.right
    elif btn == 'Button.middle':
        return pynput.mouse.Button.middle
    return pynput.mouse.Button.unknown
