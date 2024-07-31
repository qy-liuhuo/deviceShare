# from src.sharer.server import Server
# from src.sharer.client import Client
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QColor, QPalette, QLinearGradient
import sys


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 550)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(160, 400, 111, 61))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(150, 230, 150, 151))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radioButton_2 = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.radioButton_2.setFont(font)
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout.addWidget(self.radioButton_2)
        self.radioButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.radioButton.setFont(font)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout.addWidget(self.radioButton)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(150, 160, 161, 61))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(70, 50, 311, 91))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "进入"))
        self.radioButton_2.setText(_translate("Dialog", "主控机"))
        self.radioButton.setText(_translate("Dialog", "受控机"))
        self.label.setText(_translate("Dialog", "选择角色"))
        self.label_2.setText(_translate("Dialog", "device share"))


class welcome(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setGradientBackground()
        self.ui.pushButton.clicked.connect(self.selectRole)

    def setGradientBackground(self):
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 220)
        gradient.setColorAt(0, QColor(50, 50, 50))  # 深色
        gradient.setColorAt(1, QColor(255, 255, 255))  # 白色

        palette.setBrush(QPalette.Background, gradient)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    # todo: 接入现有的server和client逻辑
    def selectRole(self):
        if self.ui.radioButton.isChecked():
            # client = Client()
            self.hide()
        elif self.ui.radioButton_2.isChecked():
            # server = Server()
            self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MyDialog = welcome()
    MyDialog.show()
    sys.exit(app.exec())
