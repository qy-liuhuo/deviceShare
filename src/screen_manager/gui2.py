import enum
import sys
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox, QToolBar, QLabel, QVBoxLayout, \
    QWidget, QSystemTrayIcon, QStyle
from PyQt5.QtGui import QIcon

class GuiMessage:
    class MessageType(enum.IntEnum):
        ACCESS_REQUIRE = enum.auto()
        ACCESS_RESPONSE = enum.auto()
    def __init__(self, msg_type, data):
        self.msg_type = msg_type
        self.data = data

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeviceShare')
        self.setWindowIcon(
            QIcon("D:\\Project\\PythonProject\\DeviceShare\\resources\\devicelink.ico"))  # 确保你的项目目录下有一个icon.png文件
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

        # self.mainWin.show()

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
            self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Critical, 5000)
        self.trayIcon.showMessage("申请", "设备" + device_id + "申请加入链接,点击处理", QSystemTrayIcon.Information, 5000)

if __name__ == '__main__':
    gui = Gui2()
    gui.run()
