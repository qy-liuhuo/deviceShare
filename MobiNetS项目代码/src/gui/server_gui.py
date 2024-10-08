"""
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: MobiNets
"""
import enum
import os
import sys
import time
from threading import Thread

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QStringListModel, Qt, QTimer, QFileInfo, QRect, pyqtProperty, QPropertyAnimation, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox, QToolBar, QLabel, QVBoxLayout, \
    QWidget, QSystemTrayIcon, QStyle, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QGraphicsEffect, QListView, \
    QStyledItemDelegate, QPushButton, QDialog, QCheckBox, QSpinBox, QDialogButtonBox, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QColor, QBrush, QPalette, QStandardItem, QStandardItemModel, QFont, QPainter, \
    QPainterPath, QCursor, QPen
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PIL import Image, ImageDraw, ImageFont
import qt_material
from src.gui.position import Position
from src.utils.device_storage import DeviceStorage
from src.utils.key_storage import KeyStorage

DEFAULT_WIDTH = 384
DEFAULT_HEIGHT = 216


class GuiMessage:
    """
    GuiMessage class to store message information
    """
    class MessageType(enum.IntEnum):
        """
        MessageType class to store message type
        """
        ACCESS_REQUIRE = enum.auto() # 申请连接
        ACCESS_RESPONSE = enum.auto() # 连接响应

    def __init__(self, msg_type, data):
        """
        初始化
        :param msg_type: 消息类型
        :param data: 数据
        """
        self.msg_type = msg_type
        self.data = data


class ShareConfigurationInterface(QDialog):
    def __init__(self, parent):
        super().__init__()

        self.setFixedSize(400, 350)

        self.setWindowTitle("共享选项设置")
        self.parent = parent
        # self.setParent(parent)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        qr = self.frameGeometry()  # 获取对话框的几何框架
        cp = QApplication.primaryScreen().availableGeometry().center()  # 获取屏幕中心点
        qr.moveCenter(cp)  # 将对话框几何框架的中心移动到屏幕中心
        self.move(qr.topLeft())  # 将对话框的左上角移动到新的位置
        self.share_keyboard = QCheckBox("共享键盘")
        self.share_clipboard = QCheckBox("共享剪切板")
        self.share_file = QCheckBox("共享文件")
        self.encryption = QCheckBox("加密传输")
        self.transmission_granularity = QSpinBox()  # 传输粒度
        self.transmission_granularity.setMinimum(1)
        self.transmission_granularity.setMaximum(10)
        spinLayout = QHBoxLayout()
        label = QLabel("传输粒度")
        spinLayout.addWidget(label)
        spinLayout.addWidget(self.transmission_granularity)
        self.share_keyboard.setStyleSheet("font-size: 24px;")
        self.share_clipboard.setStyleSheet("font-size: 24px;")
        self.share_file.setStyleSheet("font-size: 24px;")
        self.encryption.setStyleSheet("font-size: 24px;")
        self.transmission_granularity.setStyleSheet("font-size: 24px;height:40px;")
        label.setStyleSheet("font-size: 24px;")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.submit)
        self.button_box.rejected.connect(self.hide)

        self.layout.addWidget(self.share_keyboard)
        self.layout.addWidget(self.share_clipboard)
        self.layout.addWidget(self.share_file)
        self.layout.addWidget(self.encryption)
        # self.layout.addWidget(self.transmission_granularity)
        self.layout.addLayout(spinLayout)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

        self.configuration = None
        self.hide()

    def setData(self, config):
        self.configuration = config
        self.share_keyboard.setChecked(self.configuration["shareKeyBoard"])
        self.share_clipboard.setChecked(self.configuration["shareClipBoard"])
        self.share_file.setChecked(self.configuration["shareFile"])
        self.encryption.setChecked(self.configuration["encryption"])
        self.transmission_granularity.setValue(self.configuration["transmissionGranularity"])

    def submit(self):
        self.configuration["shareKeyBoard"] = self.share_keyboard.isChecked()
        self.configuration["shareClipBoard"] = self.share_clipboard.isChecked()
        self.configuration["shareFile"] = self.share_file.isChecked()
        self.configuration["encryption"] = self.encryption.isChecked()
        self.configuration["transmissionGranularity"] = self.transmission_granularity.value()
        self.hide()


class ClientScreen(QLabel):
    """
    ClientScreen class to store client screen information
    """
    def __init__(self, master, x, y, location, *__args):
        """
        初始化
        :param master: 主窗口
        :param x: x
        :param y: y
        :param location: 位置
        :param __args: 参数
        """
        super().__init__(master, *__args)
        self.master = master
        # self.client_ip = ""
        # self.empty = True
        self.device_id = ""
        self._x = x
        self._y = y
        self.isMoving = False
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.location = location
        self.setAcceptDrops(True)
        self.setFrameShape(QtWidgets.QFrame.Box)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.create_menu)
        self.setStyleSheet('border-width: 0px;border-style: solid;border-color: black;border-radius: 12')
        self.setAlignment(QtCore.Qt.AlignVCenter)
        self.move(x, y)

    def set_client(self, device_id):
        """
        设置客户端
        :param device_id:  设备id
        :return:
        """
        original_client = self.device_id
        self.device_id = device_id
        if device_id == "":
            self.setPixmap(QPixmap(""))
        else:
            self.setPixmap(self.create_round_pixmap(device_id[:10]))
        return original_client

    def mousePressEvent(self, e):
        """
        鼠标按下事件
        :param e:
        :return:
        """
        if e.buttons() == QtCore.Qt.LeftButton:
            if self.device_id != "":
                self.isMoving = True
                self.relative_position = e.pos()
                self.master.prepare_modify(self)

    def mouseMoveEvent(self, e):
        """
        鼠标移动事件
        :param e:
        :return:
        """
        if e.buttons() == QtCore.Qt.LeftButton:
            if self.device_id != "":
                self.move(self.mapToParent(e.pos()) - self.relative_position)
                self.master.track_move(self.x(), self.y())

    def mouseReleaseEvent(self, e):
        """
        鼠标释放事件
        :param e:
        :return:
        """
        if self.isMoving:
            self.master.finish_modify(self.x(), self.y(), self)
            self.setParent(None)
            self.deleteLater()
            self.isMoving = False

    def enter(self):
        """
        进入
        :return:
        """
        if self.device_id != "":
            self.setPixmap(QPixmap(""))
        self.setStyleSheet('border-width: 2px;border-style: solid;border-color:  #0984e3;;border-radius: 9')

    def leave(self):
        """
        离开
        :return:
        """
        if self.device_id != "":
            self.setPixmap(self.create_round_pixmap(self.device_id[:10]))
            self.set_opacity(0.5)
        self.setStyleSheet('border-width: 0px;border-style: solid;border-color: black;border-radius: 9')

    def create_menu(self):
        """
        创建菜单
        :return:
        """
        if self.device_id != "":
            self.menu = QMenu(self)

            self.delete = QAction(u'强制下线', self)  # 创建菜单选项对象
            # self.actionA.setShortcut('del')  # 设置动作A的快捷键
            self.menu.addAction(self.delete)  # 把动作A选项对象添加到菜单self.groupBox_menu上
            self.delete.triggered.connect(self.device_offline)
            self.menu.popup(QCursor.pos())

    def device_offline(self):
        """
        设备下线
        :return:
        """
        sqlWriter = DeviceStorage()
        sqlWriter.delete_device(self.device_id)
        sqlWriter.close()
        QMessageBox.information(self, "DeviceShare", "设备" + self.device_id + "已强制下线", QMessageBox.Ok)
        self.master.client_init()

    def set_opacity(self, opacity):
        """
        设置透明度
        :param opacity:
        :return:
        """
        effect_opacity = QGraphicsOpacityEffect()
        effect_opacity.setOpacity(opacity)
        self.setGraphicsEffect(effect_opacity)

    def create_round_pixmap(self, device_id):
        """
        创建圆形图片
        :param device_id:   设备id
        :return:
        """
        if not os.path.exists("./temp/"):
            os.makedirs("./temp/")
        if not QFileInfo('./temp/' + device_id + ".jpg").exists():
            self.new_image(device_id)
        pixmap = QPixmap("./temp/" + device_id + ".jpg")
        size = self.size()
        rounded_pixmap = QPixmap(size)
        rounded_pixmap.fill(Qt.transparent)

        painter = QPainter(rounded_pixmap)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), 9, 9)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded_pixmap

    def new_image(self, device_id):
        """
        创建新图片
        :param device_id:  设备id
        :return:
        """
        font = ImageFont.truetype('resources/GenJyuuGothic-Normal.ttf', 30)
        w, h = font.getsize(device_id)
        H = DEFAULT_HEIGHT
        W = DEFAULT_WIDTH
        img = Image.new('RGB', (DEFAULT_WIDTH, DEFAULT_HEIGHT), (116, 125, 140))
        drawer = ImageDraw.Draw(img)

        # def draw_round_rectangle(x, y, w, h, r):
        #     drawer.ellipse((x, y, x + r * 2, y + r * 2), fill="gray")
        #     drawer.ellipse((x + w - r * 2, y, x + w, y + r * 2), fill="gray")
        #     drawer.ellipse((x, y + h - r * 2, x + r * 2, y + h), fill="gray")
        #     drawer.ellipse((x + w - r * 2, y + h - r * 2, x + w, y + h), fill="gray")
        #     drawer.rectangle((x + r, y, x + w - r, y + h), fill="gray")
        #     drawer.rectangle((x, y + r, x + w, y + h - r), fill="gray")
        # # draw_round_rectangle(x=(W - w) / 2 - 30, y=(H - h) / 2 - 20, w=w + 60, h=h + 40, r=30)
        drawer.text(((W - w) / 2, (H - h) / 2), device_id, (255, 255, 255), font=font)
        img.save("./temp/" + device_id + ".jpg")


class ClientList(QListView):
    """
    ClientList class to store client list
    """
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.model = QStandardItemModel(self)
        self.init()

    def init(self):
        """
        初始化
        :return:
        """
        class CustomDelegate(QStyledItemDelegate):
            def paint(self, painter, option, index):
                # 设置文本居中对齐
                option.displayAlignment = Qt.AlignCenter
                super().paint(painter, option, index)

            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(40)
                return size

        self.raise_()
        self.setItemDelegate(CustomDelegate(self))
        self.setGeometry(0, 0, 312, 300)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.create_menu)
        self.hide()

    def update_data(self):
        """
        更新数据
        :return:
        """
        deviceReader = DeviceStorage()
        device_list = deviceReader.get_all_devices()
        deviceReader.close()
        online_devices = []
        self.model.clear()
        for device in device_list:
            text = device.device_id + " -在线"
            new_item = QStandardItem(text)
            self.model.appendRow(new_item)
            online_devices.append(device.device_id)
        keyReader = KeyStorage()
        key_name_list = keyReader.get_all_key_name()
        keyReader.close()
        offline_devices = list(filter(lambda key_name: key_name not in online_devices, key_name_list))
        for device_id in offline_devices:
            text = device_id + " -离线"
            new_item = QStandardItem(text)
            self.model.appendRow(new_item)
        self.setModel(self.model)

    def mousePressEvent(self, e):
        """
        鼠标按下事件
        :param e:
        :return:
        """
        if e.buttons() == QtCore.Qt.RightButton:
            index = self.indexAt(e.pos())
            if index.isValid():
                # 如果是有效的item区域内点击，则调用父类的mousePressEvent处理
                super().mousePressEvent(e)
                self.create_menu()

    def create_menu(self):
        """
        创建菜单
        :return:
        """
        index = self.currentIndex()
        if index:
            menu = QMenu(self)
            action_delete = QAction("删除", self)
            menu.addAction(action_delete)
            action_delete.triggered.connect(self.delete_item)
            menu.exec_(QCursor.pos())

    def delete_item(self):
        """
        删除item
        :return:
        """
        index = self.currentIndex()
        keyWriter = KeyStorage()
        id = index.data().split()[0]
        keyWriter.delete_key(id)
        keyWriter.close()
        deviceWriter = DeviceStorage()
        if deviceWriter.get_device(id):
            deviceWriter.delete_device(id)
        deviceWriter.close()
        self.master.client_init()
        QMessageBox.information(self, "DeviceShare", "设备" + id + "已被删除", QMessageBox.Ok)


class ConfigurationInterface(QWidget):
    """
    ConfigurationInterface class to store configuration interface
    """
    def __init__(self, master, update_flag):
        """
        初始化
        :param master:
        :param update_flag:
        """
        super().__init__(master)
        self.update_flag = update_flag
        self.last_potential_location = None
        self.resize(1250, 850)
        self.center_image = QLabel("", self)
        self.center_image.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.center_image.setStyleSheet('border-width: 0px;border-style: solid;border-color: black;border-radius: 12')
        self.center_image.setPixmap(self.create_round_pixmap())
        self.center_image.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.center_image.move(int(self.width() / 2 - self.center_image.width() / 2),
                               int(self.height() / 2 - self.center_image.height() / 2))
        self.client_list = ClientList(self)
        self.clients = {
            Position["TOP"]: ClientScreen(self, self.center_image.x(), self.center_image.y() - DEFAULT_HEIGHT - 10,
                                          Position["TOP"]),
            Position["LEFT"]: ClientScreen(self, self.center_image.x() - DEFAULT_WIDTH - 10, self.center_image.y(),
                                           Position["LEFT"]),
            Position["RIGHT"]: ClientScreen(self, self.center_image.x() + DEFAULT_WIDTH + 10, self.center_image.y(),
                                            Position["RIGHT"]),
            Position["BOTTOM"]: ClientScreen(self, self.center_image.x(), self.center_image.y() + DEFAULT_HEIGHT + 10,
                                             Position["BOTTOM"])}
        self.client_init()
        self.done = QPushButton(self, text="确认")
        self.done.setGeometry(600, 810, 110, 60)
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.done.setFont(font)
        self.done.clicked.connect(self.save_configuration)
        self.done.setStyleSheet('border-width: 1px;border-style: solid;border-color: black;border-radius: 8')
        # self.online_update()
        self.show()

    def client_init(self):
        """
        客户端初始化
        :return:
        """
        # device_dict = {}
        sqlReader = DeviceStorage()
        device_list = sqlReader.get_all_devices()
        sqlReader.close()
        for screen in self.clients.values():
            screen.set_client("")
        for device in device_list:
            self.clients[device.position].set_client(device.device_id)
        self.client_list.update_data()

    def prepare_modify(self, currentClient):
        """
        准备修改
        :param currentClient:
        :return:
        """
        for client in self.clients.values():
            if currentClient != client and client.device_id != "":
                client.set_opacity(0.5)
        tempScreen = ClientScreen(self, currentClient.x(), currentClient.y(), currentClient.location)
        tempScreen.show()
        self.clients[currentClient.location] = tempScreen

    def track_move(self, x, y):
        """
        跟踪移动
        :param x:
        :param y:
        :return:
        """
        potential_target_location = self.get_target_location(x, y)
        if potential_target_location != self.last_potential_location:
            if self.last_potential_location:
                self.clients[self.last_potential_location].leave()
            self.last_potential_location = potential_target_location
            if self.last_potential_location:
                self.clients[self.last_potential_location].enter()

    def finish_modify(self, x, y, current_client):
        """
        完成修改
        :param x:
        :param y:
        :param current_client:
        :return:
        """
        if self.last_potential_location:
            self.clients[self.last_potential_location].leave()
        self.last_potential_location = None
        for client in self.clients.values():
            if client.device_id != "":
                client.set_opacity(1)
        target_location = self.get_target_location(x, y)
        if not target_location:
            target_location = current_client.location
        exchange_ip = self.clients[target_location].set_client(current_client.device_id)
        if target_location != current_client.location:
            self.clients[current_client.location].set_client(exchange_ip)

    def get_target_location(self, x, y):
        """
        获取目标位置
        :param x:
        :param y:
        :return:
        """
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

    def display_client_list(self):
        """
        显示客户端列表
        :return:
        """
        if self.client_list.isVisible():
            self.client_list.hide()
        else:
            self.client_list.show()

    def save_configuration(self):
        """
        保存配置
        :return:
        """
        devices = []
        sqlReaderWriter = DeviceStorage()
        for screen in self.clients.values():
            if screen.device_id != "":
                temp = sqlReaderWriter.get_device(screen.device_id)
                if temp:
                    temp.position = screen.location
                    devices.append(temp)
        for device in devices:
            sqlReaderWriter.update_device(device)
        sqlReaderWriter.close()
        self.update_flag.set()
        QMessageBox.information(self, "DeviceShare", "配置保存成功", QMessageBox.Ok)

    def create_round_pixmap(self):
        """
        创建圆形图片
        :return:
        """
        pixmap = QPixmap("./resources/Host.jpg")  # 替换为你的图片路径
        size = self.center_image.size()
        rounded_pixmap = QPixmap(size)
        rounded_pixmap.fill(Qt.transparent)

        painter = QPainter(rounded_pixmap)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size.width(), size.height(), 9, 9)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded_pixmap

    def online_update(self, device_id):
        """
        在线更新
        :param device_id:
        :return:
        """
        for screen in self.clients.values():
            if screen.device_id == "":
                screen.set_client(device_id)
                break
        text = device_id
        new_item = QStandardItem(text)
        self.model.insertRow(0, new_item)
        self.client_list.setModel(self.model)


class MainWindow(QMainWindow):
    """
    MainWindow class to store main window
    """
    def __init__(self, config):
        super().__init__()
        self.shareConfigurationDialog = ShareConfigurationInterface(self)
        self.shareConfiguration = config
        self.initUI()

    def initUI(self):
        """
        初始化UI
        :return:
        """
        self.setWindowTitle('DeviceShare')
        self.setWindowIcon(
            QIcon("./resources/devicelink.ico"))  # 确保你的项目目录下有一个icon.png文件
        self.resize(1280, 1000)
        menubar = self.menuBar()
        authorization_list = menubar.addMenu('授权列表')
        show_list = QAction('授权列表', self)
        show_list.triggered.connect(self.show_list)
        authorization_list.addAction(show_list)
        share_configuration = QAction('共享设置', self)
        share_configuration.triggered.connect(self.show_configuration_dialog)
        menubar.addAction(share_configuration)

    def show_list(self):
        """
        显示列表
        :return:
        """
        self.configure_interface.display_client_list()

    def show_configuration_dialog(self):
        self.shareConfigurationDialog.setData(self.shareConfiguration)
        self.shareConfigurationDialog.show()

    def closeEvent(self, event):
        """
        关闭事件
        :param event:
        :return:
        """
        self.hide()
        event.ignore()

    def showEvent(self, event):
        """
        显示事件
        :param event:
        :return:
        """
        self.configure_interface.client_init()
        event.accept()

    def ask_access_require(self, id):
        """
        询问访问需求
        :param id:
        :return:
        """
        self.show()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("连接请求处理")
        msgBox.setText("是否允许设备" + id + "连接？")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setStyleSheet("QMessageBox { background-color: #000000 !important}")
        reply = msgBox.exec_()
        # msgBox.Question(None,
        #                             "连接请求处理",
        #                             "是否允许设备" + id + "连接？",
        #                             QMessageBox.Yes | QMessageBox.No)
        # self.hide()
        return reply == QMessageBox.Yes

    def set_configure_interface(self, configure_interface):
        """
        设置配置界面
        :param configure_interface:
        :return:
        """
        self.configure_interface = configure_interface


class ServerGUI:
    def __init__(self, app, update_flag, request_queue=None, response_queue=None):
        self.app = app
        self.shareConfiguration = {"shareKeyBoard": True, "shareClipBoard": True, "shareFile": True, "encryption": True, "transmissionGranularity": 5}
        self.mainWin = MainWindow(config=self.shareConfiguration)
        qt_material.apply_stylesheet(self.app, theme='light_blue.xml') # Apply the light blue theme
        self.trayIcon = QSystemTrayIcon(self.mainWin)
        self.initTrayIcon()
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.configureInterface = ConfigurationInterface(self.mainWin, update_flag)
        self.mainWin.set_configure_interface(self.configureInterface)
        self.configureInterface.setGeometry(0, 30, self.mainWin.width(), self.mainWin.height())
        self.mainWin.show()

    def initTrayIcon(self):
        """
        初始化托盘图标
        :return:
        """
        # 创建托盘图标
        self.trayIcon.setIcon(QIcon("./resources/devicelink.ico"))
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
        """
        运行
        :return:
        """
        self.app.exec_()

    def exit(self):
        """
        退出
        """
        self.trayIcon.setVisible(False)
        self.app.quit()

    def process_request(self):
        """
        处理请求
        :return:
        """
        if self.request_queue.empty():
            return
        request = self.request_queue.get()
        if request.msg_type == GuiMessage.MessageType.ACCESS_REQUIRE:
            self.response_queue.put(GuiMessage(GuiMessage.MessageType.ACCESS_RESPONSE,
                                               {"result": self.mainWin.ask_access_require(request.data["device_id"]),
                                                "device_id": request.data["device_id"]}))

    def device_offline_notify(self, device_id):
        """
        设备下线通知
        :param device_id:
        :return:
        """
        self.trayIcon.showMessage("提醒", "设备" + device_id + "已下线", QSystemTrayIcon.Information, 5000)

    def device_online_notify(self, device_id):
        """
        设备上线通知
        :param device_id:
        :return:
        """
        self.trayIcon.showMessage("提醒", "设备" + device_id + "已上线", QSystemTrayIcon.Information, 5000)

    def device_show_online_require(self, device_id):
        """
        设备显示在线需求
        :param device_id:
        :return:
        """
        if sys.platform == 'linux':
            self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Critical, 5000)
        else:
            self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Information, 5000)

    def update_devices(self):
        """
        更新设备
        :return:
        """
        self.configureInterface.client_init()


