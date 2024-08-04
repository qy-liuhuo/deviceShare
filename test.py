import pyperclip

from src.my_socket.message import Message, MsgType


new_clip_text = pyperclip.paste()
msg = Message(MsgType.CLIPBOARD_UPDATE, {'text': new_clip_text})

print(msg)