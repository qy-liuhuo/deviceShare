import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import ttkbootstrap as ttkb


class Client:
    def __init__(self, id, ip_addr, port):
        self.id = id  # 设备编号
        self.ip_addr = ip_addr
        self.port = port
        self.location = None  # 相对于主机的位置


class DraggableImage(ttkb.Frame):
    def __init__(self, master, image_path, image_id, other_image=None, center_image=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.center_image = center_image
        self.other_image = other_image
        self.image_id = image_id  # 图片编号

        self.label = ttkb.Label(self, image=self.photo)
        self.label.pack()

        if not self.center_image:
            self.label.bind('<Button-1>', self.start_move)
            self.label.bind('<B1-Motion>', self.do_move)
            self.label.bind('<ButtonRelease-1>', self.end_move)

        self.place(x=0, y=0)
        self.update_position()

    def update_position(self):
        if self.center_image:
            parent_width = self.master.winfo_width()
            parent_height = self.master.winfo_height()
            self_width = self.winfo_width()
            self_height = self.winfo_height()
            self.place(x=(parent_width - self_width) // 2, y=(parent_height - self_height) // 2)

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
                'top': (ox + (ow - iw) // 2, oy - ih),
                'bottom': (ox + (ow - iw) // 2, oy + oh),
                'left': (ox - iw, oy + (oh - ih) // 2),
                'right': (ox + ow, oy + (oh - ih) // 2)
            }

            # Find the nearest position
            min_distance = float('inf')
            nearest_position = None
            for pos in positions.values():
                distance = (self.winfo_x() - pos[0]) ** 2 + (self.winfo_y() - pos[1]) ** 2
                if distance < min_distance:
                    min_distance = distance
                    nearest_position = pos

            # Place the image at the nearest position
            self.place(x=nearest_position[0], y=nearest_position[1])

    def get_relative_position(self):
        ox, oy = self.other_image.winfo_x(), self.other_image.winfo_y()  # 中心图
        x, y = self.winfo_x(), self.winfo_y()

        if y < oy:
            return "top"
        elif y > oy:
            return "bottom"
        elif x < ox:
            return "left"
        elif x > ox:
            return "right"
        return "unknown"


def main():
    root = ttkb.Window(themename="superhero")
    root.title("主机屏幕排列")

    frame = ttkb.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    root.update_idletasks()  # Update window dimensions

    center_image = DraggableImage(frame, 'resources/background.jpg', 0, center_image=True)

    # 模拟 (后面删掉)
    client1 = Client(1, "192.168.200.130", 19999)
    client2 = Client(2, "192.168.200.131", 20000)
    client_list = [client1, client2]


    image1 = DraggableImage(frame, 'resources/background.jpg', 1, other_image=center_image)
    image2 = DraggableImage(frame, 'resources/background.jpg', 2, other_image=center_image)

    def on_done_click():
        client_list[0].location = image1.get_relative_position()  # 更新位置
        print("设备id:", client_list[0].id, "相对于主机的位置 ", client_list[0].location)
        client_list[1].location = image2.get_relative_position()  # 更新位置
        print("设备id:", client_list[1].id, "相对于主机的位置 ", client_list[1].location)
        root.destroy()

    # Done
    btn_done = ttk.Button(root, text="Done", command=on_done_click)
    btn_done.pack(side=tk.BOTTOM, padx=15, pady=15)

    root.geometry('1200x800')
    root.update()

    center_image.update_position()

    root.mainloop()


if __name__ == '__main__':
    main()
