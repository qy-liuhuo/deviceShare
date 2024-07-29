import enum
import json
import threading
import tkinter as tk
from queue import Queue
from tkinter import ttk
import pystray
from PIL import Image, ImageTk
import ttkbootstrap as ttkb
from ttkbootstrap.dialogs import MessageDialog

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
        self.location = location  # 相对于主机的位置


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

class ClientList(ttkb.Frame):
    def __init__(self, master):
        style = ttkb.Style()
        style.configure('Custom.TFrame', background='black')  # 设置背景颜色
        super().__init__(width=master.winfo_width() * 0.2, height=master.winfo_height(), style='Custom.TFrame')
        self.clientList = ttk.Treeview(master=self)
        self.clientList["columns"] = ('address')
        self.clientList.column("#0", width=0, stretch=tk.NO)
        self.clientList.column("address", anchor=ttkb.CENTER, width=self.winfo_width())
        self.clientList.heading("address", text="客户机列表")
        self.clientList.tag_configure("itemTag", background="black")
        row = self.clientList.insert(parent='', index='end', iid=0, text='',
                                     values=('192.168.3.108'))
        # self.clientList.item(row, tags="itemTag")
        self.place(x=0, y=0)
        self.clientList.place(relwidth=1, relheight=1)


def rewrite(path, client_list):
    with open(path, 'r', encoding='utf-8') as f:
        device_dict = json.load(f)
    for client in client_list:
        device_dict[client.ip_addr][2] = int(client.location)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(device_dict, f, indent=4)


class GuiMessage:
    class MessageType(enum.IntEnum):
        ACCESS_REQUIRE = enum.auto()
        ACCESS_RESPONSE = enum.auto()
    def __init__(self, msg_type, data):
        self.msg_type = msg_type
        self.data = data


class Gui:
    def __init__(self, update_func=None, gui_queue=None, server_queue=None):
        self.gui_queue = gui_queue
        self.server_queue = server_queue
        self.client_list = []
        self.image_list = []
        self.icon = None
        self.create_systray_icon()
        self.root = ttkb.Window(themename="superhero")
        self.root.title("主机屏幕排列")
        self.root.geometry('1200x800')
        self.root.update_idletasks()
        self.root.protocol('WM_DELETE_WINDOW', self.hide)
        self.frame = ttkb.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.root.update()
        self.clientList = ClientList(self.frame)
        # ttkb.Style().configure('Custom.TFrame', background='red')  # 设置背景颜色
        self.layout_interface = ttkb.Frame(master=self.frame, width=self.frame.winfo_width() * 0.8,
                                           height=self.frame.winfo_height())
        self.layout_interface.place(x=self.frame.winfo_width() * 0.2)
        self.root.update()
        self.center_image = DraggableImage(self.layout_interface, './resources/background.jpg', None, center_image=True)
        self.layout_interface.update()
        self.center_image.update_position()
        style = ttkb.Style()
        style.configure('Custom.TFrame', background='black')  # 设置背景颜色
        # self.top_frame = ttkb.Frame(self.layout_interface, width=image_size["width"], height=image_size["height"], style="Custom.TFrame")
        # self.top_frame.place(x=self.center_image.winfo_x(), y=self.center_image.winfo_y() - image_size["height"])

        self.popup = self.newPopup()
        self.popup.withdraw()

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
        self.check_queue()

    def check_queue(self):
        if not self.gui_queue.empty():
            msg = self.gui_queue.get()
            if isinstance(msg, GuiMessage):
                if msg.msg_type == GuiMessage.MessageType.ACCESS_REQUIRE:
                    self.server_queue.put(GuiMessage(GuiMessage.MessageType.ACCESS_RESPONSE,self.ask_access(msg.data['device_id'])))
        self.root.after(100, self.check_queue)

    def ask_access(self, device_id):
        self.show()
        dialog = MessageDialog(
            title="设备连接请求",
            message="是否允许新设备(" + device_id + ")连接",
            parent=None,
            alert=False,
            buttons=["拒绝:secondary", "允许:primary"],
            localize=True,
        )
        dialog.show(None)
        return dialog.result == "允许"

    def notify(self, title, message):
        self.icon.notify(title, message)

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
            client = Client(idx, device_ip, Position(device_dict[device_ip][2]))
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

    def newPopup(self):
        popup = tk.Toplevel()
        popupWidth = 450
        popupHeight = 300
        popupX = self.root.winfo_screenwidth() - popupWidth - 30
        popupY = self.root.winfo_screenheight() - popupHeight - 50
        popup.update_idletasks()

        popup.geometry(f"{popupWidth}x{popupHeight}+{popupX}+{popupY}")
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)

        popup.config(bg="white", bd=2, relief="solid")

        ttk.Style().configure("title.TFrame", background="#CAE1FF")
        title_frame = ttk.Frame(popup, width=popupWidth, height=popupHeight * 0.2)
        title_frame.configure(style="title.TFrame")
        title_frame.pack()
        titleLabel = ttk.Label(title_frame, text="主机接入认证", foreground="black", background="#CAE1FF",
                               font=tk.font.Font(size=12, family="Microsoft YaHei UI"))
        titleLabel.place(x=30, y=10)

        label = ttk.Label(popup, text="message", background="white",
                          font=tk.font.Font(size=12, family="Microsoft YaHei UI"))
        # label = ttk.Label(popup, text="message", background="white")
        # ttk.Style().configure("labelStyle", font=("Arial", 12))
        label.configure(foreground="black")
        # label.pack(pady=10)
        label.place(x=25, y=95)
        ttk.Style().configure("ButtonFrame.TFrame", background="white")
        button_frame = ttk.Frame(popup, style="ButtonFrame.TFrame")
        button_frame.configure(style="ButtonFrame.TFrame")
        button_frame.place(x=115, y=175)
        # button_frame.place_forget()
        # Microsoft YaHei UI

        ttk.Style().configure("Popup.TButton", background="white", foreground="black", highlightcolor="black", height=35,
                              font=("Microsoft YaHei UI", 12), relief="solid")

        ignore_button = ttk.Button(button_frame, text="忽略", command=popup.destroy)
        ignore_button.configure(style="Popup.TButton")
        ignore_button.pack(side=tk.RIGHT, padx=10)

        authenticate_button = ttk.Button(button_frame, text="认证", command=lambda: authenticate(popup))
        authenticate_button.configure(style="Popup.TButton")
        authenticate_button.pack(side=tk.RIGHT, padx=10)
        # ok_button.place(x=10, y=5)

        # todo: access authenticate
        def authenticate(popup):
            popup.destroy()

        return popup

    def showJoinPopup(self, ip="192.168.3.108"):
        title = self.popup.nametowidget(".!toplevel.!frame.!label")
        title["text"] = "主机接入认证"
        label = self.popup.nametowidget(f".{self.popup.winfo_name()}.!label")
        label["text"] = "主机" + ip + "请求加入"
        buttonFrame = self.popup.nametowidget(".!toplevel.!frame2")
        authenticate_button = self.popup.nametowidget(".!toplevel.!frame2.!button2")
        authenticate_button.pack(side=tk.RIGHT, padx=10)
        buttonFrame.place(x=115)
        self.popup.deiconify()

    def showOnlinePopup(self, ip="192.168.3.108"):
        title = self.popup.nametowidget(".!toplevel.!frame.!label")
        title["text"] = "主机上线通知"
        label = self.popup.nametowidget(f".{self.popup.winfo_name()}.!label")
        label["text"] = "主机" + ip + "已上线"
        buttonFrame = self.popup.nametowidget(".!toplevel.!frame2")
        authenticate_button = self.popup.nametowidget(".!toplevel.!frame2.!button2")
        authenticate_button.pack_forget()
        ok_button = self.popup.nametowidget(".!toplevel.!frame2.!button")
        ok_button["text"] = "确认"
        buttonFrame.place(x=145)
        self.popup.deiconify()



    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = Gui()
