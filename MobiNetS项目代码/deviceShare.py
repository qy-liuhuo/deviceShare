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
import logging
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton
import qt_material
from src.client import Client
from src.server import Server


class RoleSelectionDialog(QDialog):
    """
    身份选择对话框
    """
    def __init__(self):
        super().__init__()

        self.setFixedSize(400, 200)

        self.setWindowTitle("身份选择")
        self.layout = QVBoxLayout()
        qr = self.frameGeometry()  # 获取对话框的几何框架
        cp = QApplication.primaryScreen().availableGeometry().center()  # 获取屏幕中心点
        qr.moveCenter(cp)  # 将对话框几何框架的中心移动到屏幕中心
        self.move(qr.topLeft())  # 将对话框的左上角移动到新的位置
        self.server_button = QPushButton("主控机")
        self.client_button = QPushButton("被控机")

        self.layout.addWidget(self.server_button)
        self.layout.addWidget(self.client_button)

        self.setLayout(self.layout)

        self.server_button.clicked.connect(self.select_server)
        self.client_button.clicked.connect(self.select_client)

        self.selected_role = None

    def select_server(self):
        """
        选择主控机
        :return:
        """
        self.selected_role = "server"
        self.accept()

    def select_client(self):
        """
        选择被控机
        :return:
        """
        self.selected_role = "client"
        self.accept()


def main():
    logger = logging.getLogger('deviceShare')
    logger.setLevel(level=logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    logger.info("Starting DeviceShare")
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='light_blue.xml')
    selected_role = 'client'
    # 显示身份选择弹窗
    role_dialog = RoleSelectionDialog()
    if role_dialog.exec_() == QDialog.Accepted:
        selected_role = role_dialog.selected_role
    try:
        if selected_role == 'server':
            Server(app).run()
        elif selected_role == 'client':
            Client(app).run()
    except Exception as e:
        print(e)
    finally:
        app.quit()


if __name__ == "__main__":
    main()
