# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageTopics.ui'
#
# Created: Thu Jun 30 01:38:37 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_manageTopics(object):
    def setupUi(self, manageTopics):
        manageTopics.setObjectName("manageTopics")
        manageTopics.resize(392, 293)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manageTopics.setWindowIcon(icon)
        self.TopicList = QtGui.QListWidget(manageTopics)
        self.TopicList.setGeometry(QtCore.QRect(10, 20, 221, 251))
        self.TopicList.setWhatsThis("")
        self.TopicList.setResizeMode(QtGui.QListView.Adjust)
        self.TopicList.setObjectName("TopicList")
        self.line = QtGui.QFrame(manageTopics)
        self.line.setGeometry(QtCore.QRect(250, 30, 20, 231))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.layoutWidget = QtGui.QWidget(manageTopics)
        self.layoutWidget.setGeometry(QtCore.QRect(278, 21, 87, 249))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAdd = QtGui.QPushButton(self.layoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.verticalLayout.addWidget(self.btnAdd)
        self.btnRemove = QtGui.QPushButton(self.layoutWidget)
        self.btnRemove.setObjectName("btnRemove")
        self.verticalLayout.addWidget(self.btnRemove)
        spacerItem = QtGui.QSpacerItem(20, 148, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnExit = QtGui.QPushButton(self.layoutWidget)
        self.btnExit.setObjectName("btnExit")
        self.verticalLayout.addWidget(self.btnExit)

        self.retranslateUi(manageTopics)
        QtCore.QMetaObject.connectSlotsByName(manageTopics)

    def retranslateUi(self, manageTopics):
        manageTopics.setWindowTitle(QtGui.QApplication.translate("manageTopics", "Manage Topics", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("manageTopics", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("manageTopics", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("manageTopics", "Exit", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
