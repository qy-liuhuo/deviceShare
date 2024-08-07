import subprocess

def copy_to_clipboard(text):
    process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
    process.communicate(input=text.encode('utf-8'))

def paste_from_clipboard():
    process = subprocess.Popen(['wl-paste'], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')

# 示例：复制和粘贴剪贴板内容
copy_to_clipboard('Hello, Wayland!')
pasted_text = paste_from_clipboard()
print('Pasted text:', pasted_text)
