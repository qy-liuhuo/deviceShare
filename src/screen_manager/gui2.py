import enum
import json
import sys
import copy
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox, QToolBar, QLabel, QVBoxLayout, \
    QWidget, QSystemTrayIcon, QStyle, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QGraphicsEffect
from PyQt5.QtGui import QIcon, QPixmap, QColor
import qt_material
from src.screen_manager.position import Position


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
        self.setStyleSheet('border-width: 0px;border-style: dotted;border-color: black;')
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
            self.relative_position = e.pos()
            self.master.prepare_modify(self)

    def mouseMoveEvent(self, e):
        if not self.empty:
            self.move(self.mapToParent(e.pos()) - self.relative_position)
            self.master.track_move(self.x(), self.y())

    def mouseReleaseEvent(self, QMouseEvent):
        if not self.empty:
            self.master.finish_modify(self.x(), self.y(), self)
            self.setParent(None)
            self.deleteLater()

    def enter(self):
        if not self.empty:
            self.setPixmap(QPixmap(""))
        self.setStyleSheet('border-width: 2px;border-style: dotted;border-color: #0984e3;')
        self.add_shadow()

    def leave(self):
        if not self.empty:
            self.setPixmap(QPixmap("./resources/background1.jpg"))
            self.set_opacity(0.5)
        self.setStyleSheet('border-width: 0px;border-style: dotted;border-color: black;')
        self.clear_shadow()

    def set_opacity(self, opacity):
        effect_opacity = QGraphicsOpacityEffect()
        effect_opacity.setOpacity(opacity)
        self.setGraphicsEffect(effect_opacity)

    def add_shadow(self):
        effect_shadow = QGraphicsDropShadowEffect()
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(0)  # 阴影半径
        effect_shadow.setColor(QColor(255, 0, 0))
        effect_shadow.setBlurRadius(100)
        self.setGraphicsEffect(effect_shadow)

    def clear_shadow(self):
        effect_shadow = QGraphicsDropShadowEffect()
        effect_shadow.setOffset(0, 0)  # 偏移
        effect_shadow.setBlurRadius(0)  # 阴影半径
        effect_shadow.setColor(QColor(255, 0, 0))
        effect_shadow.setBlurRadius(0)
        self.setGraphicsEffect(effect_shadow)


class Client:
    def __init__(self, id, ip_addr, location=Position.NONE):
        self.id = id  # 设备编号
        self.ip_addr = ip_addr
        self.location = location


class ConfigurationInterface(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_potential_location = None
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
            client = Client(idx, device_ip,Position(device_info[2]))
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
                client.set_opacity(0.5)
        tempScreen = ClientScreen(self, currentClient.x(), currentClient.y(), currentClient.location)
        tempScreen.show()
        self.clients[currentClient.location] = tempScreen

    def track_move(self, x, y):
        potential_target_location = self.get_target_location(x, y)
        if potential_target_location != self.last_potential_location:
            if self.last_potential_location:
                self.clients[self.last_potential_location].leave()
            self.last_potential_location = potential_target_location
            if self.last_potential_location:
                self.clients[self.last_potential_location].enter()

    def finish_modify(self, x, y, current_client):
        if self.last_potential_location:
            self.clients[self.last_potential_location].leave()
        self.last_potential_location = None
        exchange_flag = False
        for client in self.clients.values():
            if not client.empty:
                client.set_opacity(1)
        target_location = self.get_target_location(x, y)
        if not target_location:
            target_location = current_client.location
        if not self.clients[target_location].set_client("./resources/background1.jpg"):
            self.clients[current_client.location].set_client("./resources/background1.jpg")

    def get_target_location(self, x, y):
        if self.center_image.y() - y > 120 and abs(x - self.center_image.x()) < 180:
            return Position["TOP"]
        elif y - self.center_image.y() > 120 and abs(x - self.center_image.x()) < 180:
            return Position["BOTTOM"]
        elif self.center_image.x() - x > 200 and abs(y - self.center_image.y()) < 100:
            return Position["LEFT"]
        elif x - self.center_image.x() > 200 and abs(y - self.center_image.y()) < 100:
            return Position["RIGHT"]
        else:
            return None


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
        qt_material.apply_stylesheet(self.app, theme='dark_blue.xml')
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
