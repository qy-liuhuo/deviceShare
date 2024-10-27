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

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow



class ClientGUI:
    """
    客户端GUI
    """
    def __init__(self,app):
        """
        初始化
        :param app:
        """
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
        """
        退出
        :return:
        """
        self.trayIcon.setVisible(False)
        self.app.quit()

    def run(self):
        """
        运行
        :return:
        """
        self.app.exec_()
