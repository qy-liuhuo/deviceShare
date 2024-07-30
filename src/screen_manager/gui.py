import json
import threading
import tkinter as tk
from tkinter import ttk

import pystray
from PIL import Image, ImageTk
import ttkbootstrap as ttkb

from src.screen_manager.position import Position


class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, text):
        if self.tip_window or not text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    tooltip = ToolTip(widget)

    def enter(event):
        tooltip.show_tip(text)

    def leave(event):
        tooltip.hide_tip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class Client:
    def __init__(self, id, ip_addr, location=Position.NONE):
        self.id = id  # 设备编号
        self.ip_addr = ip_addr
        self.location =location  # 相对于主机的位置


class DraggableImage(ttkb.Frame):
    def __init__(self, master, image_path, client, other_image=None, center_image=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.center_image = center_image
        self.other_image = other_image
        self.client = client  # 客户端

        self.label = ttkb.Label(self, image=self.photo)
        self.label.pack()

        if not self.center_image:
            self.label.bind('<Button-1>', self.start_move)
            self.label.bind('<B1-Motion>', self.do_move)
            self.label.bind('<ButtonRelease-1>', self.end_move)
            create_tooltip(self, "拓展屏幕 ip:" + self.client.ip_addr)  # 鼠标悬停提示
        if center_image:
            create_tooltip(self, "主机屏幕")
        self.place(x=0, y=0)
        self.update_position()

    def update_position(self):
        if self.center_image:
            parent_width = self.master.winfo_width()
            parent_height = self.master.winfo_height()
            self_width = self.winfo_width()
            self_height = self.winfo_height()
            self.place(x=(parent_width - self_width) // 2, y=(parent_height - self_height) // 2)
        else:
            ox, oy = self.other_image.winfo_x(), self.other_image.winfo_y()
            ow, oh = self.other_image.winfo_width(), self.other_image.winfo_height()
            iw, ih = self.winfo_width(), self.winfo_height()
            positions = {
                Position.TOP: (ox + (ow - iw) // 2, oy - ih),
                Position.BOTTOM: (ox + (ow - iw) // 2, oy + oh),
                Position.LEFT: (ox - iw, oy + (oh - ih) // 2),
                Position.RIGHT: (ox + ow, oy + (oh - ih) // 2)
            }
            self.place(x=positions[self.client.location][0], y=positions[self.client.location][1])


    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.winfo_x() - self._x + event.x
        y = self.winfo_y() - self._y + event.y
        self.place(x=x, y=y)

    def end_move(self, event):
        if self.other_image:
            ox, oy = self.other_image.winfo_x(), self.other_image.winfo_y()
            ow, oh = self.other_image.winfo_width(), self.other_image.winfo_height()
            iw, ih = self.winfo_width(), self.winfo_height()

            # Calculate positions for top, bottom, left, right
            positions = {
                'TOP': (ox + (ow - iw) // 2, oy - ih),
                'BOTTOM': (ox + (ow - iw) // 2, oy + oh),
                'LEFT': (ox - iw, oy + (oh - ih) // 2),
                'RIGHT': (ox + ow, oy + (oh - ih) // 2)
            }

            # Find the nearest position
            min_distance = float('inf')
            nearest_position = None
            for pos in positions.values():
                distance = (self.winfo_x() - pos[0]) ** 2 + (self.winfo_y() - pos[1]) ** 2
                if distance < min_distance:
                    min_distance = distance
                    nearest_position = pos

            self.place(x=nearest_position[0], y=nearest_position[1])

    def get_relative_position(self):
        ox, oy = self.other_image.winfo_x(), self.other_image.winfo_y()  # 中心图
        x, y = self.winfo_x(), self.winfo_y()

        if y < oy:
            return Position.TOP
        elif y > oy:
            return Position.BOTTOM
        elif x < ox:
            return Position.LEFT
        elif x > ox:
            return Position.RIGHT
        return Position.NONE


def rewrite(path, client_list):
    with open(path, 'r', encoding='utf-8') as f:
        device_dict = json.load(f)
    for client in client_list:
        device_dict[client.ip_addr][2] = int(client.location)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(device_dict, f, indent=4)


class Gui:

    def __init__(self,update_func=None):
        self.client_list = []
        self.image_list = []
        self.create_systray_icon()
        self.icon = None
        self.root = ttkb.Window(themename="superhero")
        self.root.title("主机屏幕排列")
        self.root.geometry('1200x800')
        self.root.update_idletasks()
        self.root.protocol('WM_DELETE_WINDOW', self.hide)
        self.frame = ttkb.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.center_image = DraggableImage(self.frame, './resources/background.jpg', None, center_image=True)

        def on_done_click():
            for i in range(len(self.client_list)):
                self.client_list[i].location = self.image_list[i].get_relative_position()  # 更新位置
                print("设备id:", self.client_list[i].id, "相对于主机的位置 ", self.client_list[i].location)
            # 将位置location写回配置文件
            rewrite("./devices.json", self.client_list)
            update_func()
            self.hide()

        # Done
        btn_done = ttk.Button(self.root, text="Done", command=on_done_click)
        btn_done.pack(side=tk.BOTTOM, padx=15, pady=15)
        self.update()
        self.hide()
        self.root.mainloop()

    def update(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.center_image = DraggableImage(self.frame, './resources/background.jpg', None, center_image=True)
        # 从配置文件中读取
        device_dict = {}
        self.client_list = []
        self.image_list = []
        try:
            with open("./devices.json", "r", encoding="utf-8") as f:
                device_dict = json.load(f)
        except Exception as e:
            print("读取配置文件失败", e)
        idx = 1
        for device_ip in device_dict:
            client = Client(idx, device_ip,Position(device_dict[device_ip][2]))
            idx = idx + 1
            self.client_list.append(client)
        for client in self.client_list:
            self.image_list.append(
                DraggableImage(self.frame, './resources/background1.jpg', client, other_image=self.center_image))
        self.root.update()
        self.center_image.update_position()

    def create_systray_icon(self):
        """
        使用 Pystray 创建系统托盘图标
        """

        # 创建图标对象
        image = Image.open("./resources/devicelink.png")  # 打开 ICO 图像文件并创建一个 Image 对象
        menu = (pystray.MenuItem(text='设置', action=self.show),  # 创建菜单项元组
                pystray.MenuItem(text='退出', action=self.quit))  # 创建菜单项元组
        self.icon = pystray.Icon("name", image, "DeviceShare", menu)  # 创建 PyStray Icon 对象，并传入关键参数
        threading.Thread(target=self.icon.run, daemon=True).start()

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.update()
        self.root.deiconify()

    def quit(self):
        # self.icon.stop()
        self.root.quit()
        self.root.destroy()


if __name__ == '__main__':
    gui = Gui()
