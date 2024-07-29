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

        # self.update_thread = Thread(target=self.listen_for_updates, daemon=True)
        # self.update_thread.start()

        # 创建列表框
        self.file_listbox = tk.Listbox(self.drop_frame)
        self.file_listbox.pack(fill="both", expand=True)

        self.file_listbox.bind("<ButtonPress-1>", self.on_listbox_press)
        self.file_listbox.bind("<B1-Motion>", self.on_listbox_move)
        self.file_listbox.bind("<ButtonRelease-1>", self.on_listbox_release)

    def on_drop(self, event):
        file_list = list(self.tk.splitlist(event.data))
        for file_path in file_list:
            if os.path.isfile(file_path) or os.path.isdir(file_path):
                file_dto = fileDto(file_path)
                self.display_file_list(file_dto)
                self.shared_queue.put(file_dto)

    def display_file_list(self, file_dto):
        display_text = f"IP: {file_dto.ip_addr}, Path: {file_dto.file_path}"
        self.file_listbox.insert(tk.END, display_text)
        self.file_list.append(file_dto.file_path)
        self.dtos.append(file_dto)
        # create_tooltip(self, file_path)  # 文件信息提示

        print(self.file_list)
        for dto in self.dtos:
            print(dto.__dict__)

    def on_listbox_press(self, event):
        # 记录初始位置
        self._drag_start_index = self.file_listbox.nearest(event.y)
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        print("executed on_icon_press")

    def on_listbox_move(self, event):
        # 拖动列表项
        delta_y = event.y - self._drag_start_y
        if abs(delta_y) > 10:  # 阈值以检测拖动
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(self._drag_start_index)
            self.file_listbox.activate(self._drag_start_index)
        print("executed on_icon_move")

    def on_listbox_release(self, event):
        # 获取列表项释放时的绝对坐标
        global_x = event.widget.winfo_rootx() - self._drag_start_x + event.x
        global_y = event.widget.winfo_rooty() - self._drag_start_y + event.y

        # 获取桌面路径 MacOs
        # 获取桌面路径
        desktop_path = self.get_desktop_path()

        print("executed on_listbox_release")
        print("global_x: ", global_x, "global_y: ", global_y)

        if global_x > 0 and global_y > 0:  # 拖出条件范围
            # 将文件复制到桌面
            selected_index = self.file_listbox.curselection()
            if selected_index:
                src_path = self.file_list[selected_index[0]]
                dst_path = os.path.join(desktop_path, os.path.basename(src_path))
                try:
                    shutil.copy2(src_path, dst_path)
                except shutil.SameFileError:
                    print(f"File already exists on desktop: {dst_path}")
                print(f"File copied to desktop: {dst_path}")

    def get_desktop_path(self):
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            return os.path.join(os.path.expanduser("~"), "Desktop")
        elif os_type == "Windows":
            return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif os_type == "Linux":
            return os.path.join(os.path.expanduser("~"), "Desktop")
        else:
            raise Exception("Unsupported operating system")

    # def on_listbox_drag_start(self, event):
    #     self.drag_data = {"x": event.x, "y": event.y, "item": self.file_listbox.nearest(event.y)}
    #
    # def on_listbox_drag_motion(self, event):
    #     delta_y = event.y - self.drag_data["y"]
    #     if abs(delta_y) > 10:
    #         self.file_listbox.selection_clear(0, tk.END)
    #         self.file_listbox.selection_set(self.drag_data["item"])
    #         self.file_listbox.activate(self.drag_data["item"])
    #
    # def on_listbox_drag_end(self, event):
    #     selected_index = self.file_listbox.curselection()
    #     if selected_index:
    #         file_path = self.file_list[selected_index[0]]
    #         self.handle_file_drag_out(file_path)
    #
    # def handle_file_drag_out(self, file_path):
    #     print(f"File {file_path} dragged out of the list")

    # def listen_for_updates(self):
    #     while True:
    #         file_dto = self.shared_queue.get()
    #         if file_dto:
    #             self.display_file_list(file_dto)


if __name__ == "__main__":
    app = FileDrag(Queue())
    app.mainloop()
