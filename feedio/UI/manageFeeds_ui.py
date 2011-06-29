# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageFeeds.ui'
#
# Created: Thu Jun 30 01:38:37 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_manageFeeds(object):
    def setupUi(self, manageFeeds):
        manageFeeds.setObjectName("manageFeeds")
        manageFeeds.resize(392, 293)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manageFeeds.setWindowIcon(icon)
        self.feedList = QtGui.QListWidget(manageFeeds)
        self.feedList.setGeometry(QtCore.QRect(10, 20, 221, 251))
        self.feedList.setWhatsThis("")
        self.feedList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.feedList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.feedList.setResizeMode(QtGui.QListView.Adjust)
        self.feedList.setObjectName("feedList")
        self.line = QtGui.QFrame(manageFeeds)
        self.line.setGeometry(QtCore.QRect(250, 30, 20, 231))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.layoutWidget = QtGui.QWidget(manageFeeds)
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

        self.retranslateUi(manageFeeds)
        QtCore.QMetaObject.connectSlotsByName(manageFeeds)

    def retranslateUi(self, manageFeeds):
        manageFeeds.setWindowTitle(QtGui.QApplication.translate("manageFeeds", "Manage Feeds", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("manageFeeds", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("manageFeeds", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("manageFeeds", "Exit", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
