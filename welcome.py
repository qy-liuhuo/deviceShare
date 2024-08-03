import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel

from src.sharer.client import Client
from src.sharer.server import Server


class RoleSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("选择身份")
        self.layout = QVBoxLayout()

        self.label = QLabel("请选择您的身份:")
        self.layout.addWidget(self.label)

        self.server_button = QPushButton("主控机")
        self.client_button = QPushButton("被控机")

        self.layout.addWidget(self.server_button)
        self.layout.addWidget(self.client_button)

        self.setLayout(self.layout)

        self.server_button.clicked.connect(self.select_server)
        self.client_button.clicked.connect(self.select_client)

        self.selected_role = None

    def select_server(self):
        self.selected_role = "server"
        self.accept()

    def select_client(self):
        self.selected_role = "client"
        self.accept()



def main():
    app = QApplication(sys.argv)
    selected_role = 'client'
    # 显示身份选择弹窗
    role_dialog = RoleSelectionDialog()
    if role_dialog.exec_() == QDialog.Accepted:
        selected_role = role_dialog.selected_role
    # 销毁 GUI
    app.exit()
    if selected_role == 'server':
        Server()
    elif selected_role == 'client':
        Client()


if __name__ == "__main__":
    main()
