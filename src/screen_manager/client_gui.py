import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow



class ClientGUI:

    def __init__(self,app):
        self.app = app
        self.window = QMainWindow()
        self.trayIcon = QSystemTrayIcon(self.window)
        self.trayIcon.setIcon(QIcon("./resources/devicelink_client.png"))
        tray_menu = QMenu(self.window)
        exitAction = QAction("退出", self.window)
        exitAction.triggered.connect(self.exit)
        tray_menu.addAction(exitAction)
        self.trayIcon.setContextMenu(tray_menu)
        self.trayIcon.show()

    def exit(self):
        self.trayIcon.setVisible(False)
        self.app.quit()

    def run(self):
        self.app.exec_()
