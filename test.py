from screeninfo import get_monitors

monitors = get_monitors()
screen_width = monitors[0].width
screen_height = monitors[0].height

print(f"屏幕宽度：{screen_width}像素")
print(f"屏幕高度：{screen_height}像素")