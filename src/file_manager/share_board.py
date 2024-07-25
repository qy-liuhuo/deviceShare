import os
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import platform
import win32con, win32gui

from src.file_manager.toolstip import create_tooltip
from fileDto import fileDto


class FileDrag(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("File Drag")
        self.geometry("280x150")

        # 设置拖放区域
        self.drop_frame = ttk.Frame(self, width=600, height=400, relief="sunken", borderwidth=2)
        self.drop_frame.pack(fill="both", expand=True)
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)

        self.file_list = []  # 保存文件路径
        self.dtos = []  # 数据传输对象

    def on_drop(self, event):
        file_list = list(self.tk.splitlist(event.data))
        for file_path in file_list:
            if os.path.isfile(file_path) or os.path.isdir(file_path):
                self.display_file_icon(file_path)

    def get_file_icon(self, file_path, icon_width=100, icon_height=100):
        icon = None
        os_type = platform.system()
        if os_type == "Darwin":
            # Mac OS
            if os.path.isfile(file_path):
                icon = Image.open(
                    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns")
            elif os.path.isdir(file_path):
                icon = Image.open(
                    "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericFolderIcon.icns")
        elif os_type == "Windows":
            if os.path.isfile(file_path):
                icon_id = win32con.IDI_APPLICATION
            else:  # Assuming it's a directory
                icon_id = win32con.IDI_DIRECTORY
            icon = win32gui.LoadIcon(0, icon_id)
            # Convert the win32 icon to PIL format
            icon = Image.frombytes('RGBA', (32, 32), win32gui.GetIconInfo(icon)[3], 'raw', 'BGRA')
        elif os_type == "Linux":
            # Linux icon handling can be very diverse depending on the environment.
            # Here we just use a placeholder approach.
            if os.path.isfile(file_path):
                icon_path = "/usr/share/icons/gnome/256x256/mimetypes/text-x-generic.png"
            elif os.path.isdir(file_path):
                icon_path = "/usr/share/icons/gnome/256x256/places/folder.png"
            try:
                icon = Image.open(icon_path)
            except FileNotFoundError:
                # Fallback if the specific icon is not found
                pass
        if icon:
            icon = icon.resize((icon_width, icon_height))
            return ImageTk.PhotoImage(icon)
        else:
            return None

    def display_file_icon(self, file_path):
        icon = self.get_file_icon(file_path)
        if icon:
            icon_frame = tk.Frame(self.drop_frame)
            icon_frame.pack(side="left", padx=5, pady=5)

            icon_label = tk.Label(icon_frame, image=icon)
            icon_label.image = icon
            icon_label.pack(side="top")

            file_name = os.path.basename(file_path)
            file_name_label = tk.Label(icon_frame, text=file_name)
            file_name_label.pack(side="bottom")

            self.file_list.append(file_path)
            self.dtos.append(fileDto(file_path))

            # create_tooltip(self, file_path)  # 文件信息提示
        print(self.file_list)
        for dto in self.dtos:
            print(dto.__dict__)


if __name__ == "__main__":
    app = FileDrag()
    app.mainloop()
