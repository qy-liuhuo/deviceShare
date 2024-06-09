import pyautogui

from MouseController import MouseController

screen_size = pyautogui.size()
print(f"屏幕大小为：{screen_size.width} x {screen_size.height}")
mouse = MouseController()
mouse.move((2610, 0))