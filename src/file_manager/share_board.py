import os
import tkinter as tk
from threading import Thread
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import platform
import shutil
from src.file_manager.toolstip import create_tooltip
from fileDto import fileDto
from queue import Queue


class FileDrag(TkinterDnD.Tk):
    def __init__(self, shared_queue):
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
        self.shared_queue = shared_queue

        self.update_thread = Thread(target=self.listen_for_updates, daemon=True)
        self.update_thread.start()

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
            import win32con, win32gui
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
            icon_path = None
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

            icon_label = tk.Label(icon_frame, image=icon, text=os.path.basename(file_path), compound="top")
            icon_label.image = icon
            icon_label.file_path = file_path
            icon_label.pack(side="top")
            icon_label.bind("<ButtonPress-1>", self.on_icon_press)
            icon_label.bind("<B1-Motion>", self.on_icon_move)
            icon_label.bind("<ButtonRelease-1>", self.on_icon_release)

            self.file_list.append(file_path)
            self.dtos.append(fileDto(file_path))

            # create_tooltip(self, file_path)  # 文件信息提示
        print(self.file_list)
        for dto in self.dtos:
            print(dto.__dict__)

    def on_icon_press(self, event):
        # 记录初始位置
        event.widget._drag_start_x = event.x
        event.widget._drag_start_y = event.y
        print("executed on_icon_press")

    def on_icon_move(self, event):
        # 拖动图标
        x = event.widget.winfo_x() - event.widget._drag_start_x + event.x
        y = event.widget.winfo_y() - event.widget._drag_start_y + event.y

        event.widget.place(x=x, y=y)
        print("executed on_icon_move")

    def on_icon_release(self, event):
        # 获取图标释放时的绝对坐标
        global_x = event.widget.winfo_rootx() - event.widget._drag_start_x + event.x
        global_y = event.widget.winfo_rooty() - event.widget._drag_start_y + event.y

        # 获取桌面路径 MacOs
        desktop_path = None
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        elif os_type == "Windows":
            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif os_type == "Linux":
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            raise Exception("Unsupported operating system")

        print("executed on_icon_release")
        print("global_x: ", global_x, "global_y: ", global_y)

        if global_x > 0 and global_y > 0:  # ??? 拖出条件范围
            # 将文件复制到桌面
            src_path = event.widget.file_path
            dst_path = os.path.join(desktop_path, os.path.basename(src_path))
            try:
                shutil.copy2(src_path, dst_path)
            except shutil.SameFileError:
                print(f"File already exists on desktop: {dst_path}")
            print(f"File copied to desktop: {dst_path}")

    def listen_for_updates(self):
        while True:
            file_dto = self.shared_queue.get()
            if file_dto:
                self.display_file_icon(file_dto.file_path)


if __name__ == "__main__":
    app = FileDrag(Queue())
    app.mainloop()
