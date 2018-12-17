# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(80, 110, 231, 71))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.password = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 3, 1, 1, 1)
        self.employid = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.employid.setObjectName("employid")
        self.gridLayout.addWidget(self.employid, 1, 1, 1, 1)
        self.login = QtWidgets.QPushButton(Form)
        self.login.setGeometry(QtCore.QRect(240, 220, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.login.setFont(font)
        self.login.setObjectName("login")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 371, 51))
        font = QtGui.QFont()
        font.setPointSize(23)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("background-image: url(:/carsnapshot/image/jihuo5.jpg);")
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "欢迎使用绿通大数据辅助检测App"))
        self.label.setText(_translate("Form", "工号"))
        self.label_2.setText(_translate("Form", "密码"))
        self.login.setText(_translate("Form", "登录"))
        self.label_3.setText(_translate("Form", " SunshineLvtong WelCome"))

from ui import lvtong_rc
