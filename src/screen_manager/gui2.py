import enum
import json
import sys
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox, QToolBar, QLabel, QVBoxLayout, \
    QWidget, QSystemTrayIcon, QStyle, QGraphicsOpacityEffect
from PyQt5.QtGui import QIcon, QPixmap

from position import Position

DEFAULT_WIDTH = 384
DEFAULT_HEIGHT = 216


class GuiMessage:
    class MessageType(enum.IntEnum):
        ACCESS_REQUIRE = enum.auto()
        ACCESS_RESPONSE = enum.auto()

    def __init__(self, msg_type, data):
        self.msg_type = msg_type
        self.data = data


class ClientScreen(QLabel):
    def __init__(self, master, x, y, location, *__args):
        super().__init__(master, *__args)
        self.master = master
        self.empty = True
        self._x = x
        self._y = y
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.location = location
        self.setAcceptDrops(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setStyleSheet('border-width: 1px;border-style: solid;border-color: black;')

        # 调整文字与边框的对齐，可以多试几个参数，比如AlignTop
        self.setAlignment(QtCore.Qt.AlignVCenter)
        self.move(x, y)

    def set_client(self, image_path):
        # todo: need to return ip message of client
        # original_client = None
        flag = self.empty
        self.setPixmap(QPixmap(image_path))
        self.empty = False
        return flag

    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton and not self.empty:
            # self.setPixmap(QPixmap(""))
            self.relative_position = e.pos()
            self.master.prepare_modify(self)

    def mouseMoveEvent(self, e):
        if not self.empty:
            self.move(self.mapToParent(e.pos()) - self.relative_position)
        # self.move(self.mapToParent(e.pos()) - self.relative_position)

    def mouseReleaseEvent(self, QMouseEvent):
        target_location, needExchange = self.master.finish_modify(self.x(), self.y())
        if target_location and target_location != self.location:
            self.setPixmap(QPixmap(""))
        if needExchange:
            self.setPixmap(QPixmap("./resources/background1.jpg"))
        self.move(self._x, self._y)


class Client:
    def __init__(self, id, ip_addr, location="NONE"):
        self.id = id  # 设备编号
        self.ip_addr = ip_addr
        self.location = Position[location]


class ConfigurationInterface(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(1250, 850)
        self.setWindowTitle('主机屏幕排列')
        self.center_image = QLabel("", self)
        self.center_image.setPixmap(QPixmap("./resources/background.jpg"))
        self.center_image.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.center_image.move(int(self.width() / 2 - self.center_image.width() / 2),
                               int(self.height() / 2 - self.center_image.height() / 2))
        self.client_init()
        self.show()

    def client_init(self):
        self.clients = {
            Position["TOP"]: ClientScreen(self, self.center_image.x(), self.center_image.y() - DEFAULT_HEIGHT - 10,
                                          Position["TOP"]),
            Position["LEFT"]: ClientScreen(self, self.center_image.x() - DEFAULT_WIDTH - 10, self.center_image.y(),
                                           Position["LEFT"]),
            Position["RIGHT"]: ClientScreen(self, self.center_image.x() + DEFAULT_WIDTH + 10, self.center_image.y(),
                                            Position["RIGHT"]),
            Position["BOTTOM"]: ClientScreen(self, self.center_image.x(), self.center_image.y() + DEFAULT_HEIGHT + 10,
                                             Position["BOTTOM"])}
        # device_dict = {}
        with open("./devices.json", "r", encoding="utf-8") as f:
            device_dict = json.load(f)
        client_list = []
        idx = 1
        for device_ip, device_info in device_dict.items():
            client = Client(idx, device_ip, device_info[2].split(".")[1])
            idx = idx + 1
            client_list.append(client)
        for client in client_list:
            self.clients[client.location].set_client('resources/background1.jpg')

    def place_client_screen(self, client_image, location):
        if location == Position["LEFT"]:
            client_image.move(self.center_image.x() - DEFAULT_WIDTH - 10, self.center_image.y())
        if location == Position["RIGHT"]:
            client_image.move(self.center_image.x() + DEFAULT_WIDTH + 10, self.center_image.y())
        if location == Position["TOP"]:
            client_image.move(self.center_image.x(), self.center_image.y() - DEFAULT_HEIGHT - 10)
        if location == Position["BOTTOM"]:
            client_image.move(self.center_image.x(), self.center_image.y() + DEFAULT_HEIGHT + 10)

        # todo: how to process if location is None?

    def prepare_modify(self, currentClient):
        for client in self.clients.values():
            if currentClient != client and not client.empty:
                opacity_effect = QGraphicsOpacityEffect()
                opacity_effect.setOpacity(0.5)
                client.setGraphicsEffect(opacity_effect)

    def finish_modify(self, x, y):
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(1)
        exchange_flag = False
        for client in self.clients.values():
            if not client.empty:
                client.setGraphicsEffect(opacity_effect)
        if self.center_image.y() - y > 120 and abs(x - self.center_image.x()) < 180:
            target_location = Position["TOP"]
            # if not self.clients[Position["TOP"]].set_client("./resources/background1.jpg"):
            #
            # return Position["TOP"]
        elif y - self.center_image.y() > 120 and abs(x - self.center_image.x()) < 180:
            target_location = Position["BOTTOM"]
            # self.clients[Position["BOTTOM"]].set_client("./resources/background1.jpg")
            # return Position["BOTTOM"]
        elif self.center_image.x() - x > 200 and abs(y - self.center_image.y()) < 100:
            target_location = Position["LEFT"]
            # self.clients[Position["LEFT"]].set_client("./resources/background1.jpg")
            # return Position["LEFT"]
        elif x - self.center_image.x() > 200 and abs(y - self.center_image.y()) < 100:
            target_location = Position["RIGHT"]
            # self.clients[Position["RIGHT"]].set_client("./resources/background1.jpg")
            # return Position["RIGHT"]
        else:
            target_location = None
        if not self.clients[target_location].set_client("./resources/background1.jpg"):
            exchange_flag = True
        return target_location, exchange_flag


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeviceShare')
        self.setWindowIcon(
            QIcon("./resources/devicelink.ico"))  # 确保你的项目目录下有一个icon.png文件
        self.resize(1400, 1000)
        menubar = self.menuBar()
        authorization_list = menubar.addMenu('授权列表')

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def ask_access_require(self, id):
        self.show()
        reply = QMessageBox.information(None,
                                        "连接请求处理",
                                        "是否允许设备" + id + "连接？",
                                        QMessageBox.Yes | QMessageBox.No)
        self.hide()
        return reply == QMessageBox.Yes


class Gui2:
    def __init__(self, update_func=None, request_queue=None, response_queue=None):
        self.app = QApplication(sys.argv)
        self.mainWin = MainWindow()
        self.trayIcon = QSystemTrayIcon(self.mainWin)
        self.initTrayIcon()
        self.request_queue = request_queue
        self.response_queue = response_queue

        self.configureInterface = ConfigurationInterface(self.mainWin)
        self.configureInterface.setGeometry(0, 40, self.mainWin.width(), self.mainWin.height() - 40)

        self.mainWin.show()

    def initTrayIcon(self):
        # 创建托盘图标
        self.trayIcon.setIcon(QIcon("D:\\Project\\PythonProject\\DeviceShare\\resources\\devicelink.ico"))
        # 创建托盘菜单
        trayMenu = QMenu(self.mainWin)
        # 添加显示窗口动作
        showSetting = QAction('设置', self.mainWin)
        showSetting.triggered.connect(self.mainWin.show)
        trayMenu.addAction(showSetting)
        # 添加退出动作
        exitAction = QAction('退出', self.mainWin)
        exitAction.triggered.connect(self.exit)
        trayMenu.addAction(exitAction)
        # 将菜单添加到托盘图标
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.messageClicked.connect(self.process_request)
        # 显示托盘图标
        self.trayIcon.show()

    def run(self):
        self.app.exec_()

    def exit(self):
        self.trayIcon.setVisible(False)
        self.app.quit()

    def process_request(self):
        # if self.request_queue.empty():
        #     return
        # request = self.request_queue.get()
        # if request.msg_type == GuiMessage.MessageType.ACCESS_REQUIRE:
        #     self.response_queue.put(GuiMessage(GuiMessage.MessageType.ACCESS_RESPONSE, {"result":self.mainWin.ask_access_require(request.data["device_id"]), "device_id":request.data["device_id"]}))
        print(self.mainWin.ask_access_require("123"))
        self.response_queue.put(GuiMessage(GuiMessage.MessageType.ACCESS_RESPONSE,
                                           {"result": True,
                                            "device_id": "qwe"}))
        # reply = QMessageBox.question(self.mainWin,
        #                      "连接请求处理",
        #                      "是否允许设备" + id + "连接？",
        #                      QMessageBox.Yes | QMessageBox.No)
        # self.response_queue.put(GuiMessage(GuiMessage.MessageType.ACCESS_RESPONSE, {"result":reply == QMessageBox.Yes, "device_id":id}))

    def device_offline_notify(self, device_id):
        self.trayIcon.showMessage("提醒", "设备" + device_id + "已下线", QSystemTrayIcon.Information, 5000)

    def device_online_notify(self, device_id):
        self.trayIcon.showMessage("提醒", "设备" + device_id + "已上线", QSystemTrayIcon.Information, 5000)

    def device_show_online_require(self, device_id):
        if (sys.platform == 'Linux'):
            self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Critical,
                                      5000)
        self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Information,
                                  5000)


if __name__ == '__main__':
    gui = Gui2()
    gui.run()
