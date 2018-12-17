# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sqlmode.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(912, 641)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(30, 20, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.execsql = QtWidgets.QPushButton(Form)
        self.execsql.setGeometry(QtCore.QRect(730, 20, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.execsql.setFont(font)
        self.execsql.setObjectName("execsql")
        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(100, 70, 891, 491))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.displayresult = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.displayresult.setContentsMargins(0, 0, 0, 0)
        self.displayresult.setObjectName("displayresult")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(110, 19, 611, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setGeometry(QtCore.QRect(680, 580, 221, 23))
        self.progressBar.setMaximum(98)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(580, 580, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "数据库模式"))
        self.label.setText(_translate("Form", "Sql语句"))
        self.execsql.setText(_translate("Form", "执行"))
        self.label_2.setText(_translate("Form", "执行进度"))

