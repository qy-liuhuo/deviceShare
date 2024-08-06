import pynput
with pynput.mouse.Events() as events:
    for event in events:
        if isinstance(event, pynput.mouse.Events.Move):
            x, y = event.x, event.y
            print(x,y)