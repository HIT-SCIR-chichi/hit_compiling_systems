# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'semantic_info.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(960, 540)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../help/system.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 15, 0, 0)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grammar_label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.grammar_label.setFont(font)
        self.grammar_label.setAlignment(QtCore.Qt.AlignCenter)
        self.grammar_label.setObjectName("grammar_label")
        self.verticalLayout.addWidget(self.grammar_label)
        self.grammar_tbl = QtWidgets.QTableWidget(self.frame)
        self.grammar_tbl.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.grammar_tbl.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.grammar_tbl.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.grammar_tbl.setObjectName("grammar_tbl")
        self.grammar_tbl.setColumnCount(1)
        self.grammar_tbl.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.grammar_tbl.setHorizontalHeaderItem(0, item)
        self.verticalLayout.addWidget(self.grammar_tbl)
        self.horizontalLayout.addWidget(self.frame)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "语义信息"))
        self.grammar_label.setText(_translate("Dialog", "文法"))
        item = self.grammar_tbl.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "产生式"))
