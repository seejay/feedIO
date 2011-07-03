# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageFeeds.ui'
#
# Created: Sun Jul  3 13:11:34 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_manageFeeds(object):
    def setupUi(self, manageFeeds):
        manageFeeds.setObjectName("manageFeeds")
        manageFeeds.resize(392, 293)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manageFeeds.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(manageFeeds)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.urlLine = QtGui.QLineEdit(manageFeeds)
        self.urlLine.setObjectName("urlLine")
        self.verticalLayout_2.addWidget(self.urlLine)
        self.feedList = QtGui.QListWidget(manageFeeds)
        self.feedList.setWhatsThis("")
        self.feedList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.feedList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.feedList.setResizeMode(QtGui.QListView.Adjust)
        self.feedList.setObjectName("feedList")
        self.verticalLayout_2.addWidget(self.feedList)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.line = QtGui.QFrame(manageFeeds)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAdd = QtGui.QPushButton(manageFeeds)
        self.btnAdd.setObjectName("btnAdd")
        self.verticalLayout.addWidget(self.btnAdd)
        self.btnRemove = QtGui.QPushButton(manageFeeds)
        self.btnRemove.setObjectName("btnRemove")
        self.verticalLayout.addWidget(self.btnRemove)
        spacerItem = QtGui.QSpacerItem(20, 148, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnExit = QtGui.QPushButton(manageFeeds)
        self.btnExit.setObjectName("btnExit")
        self.verticalLayout.addWidget(self.btnExit)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(manageFeeds)
        QtCore.QMetaObject.connectSlotsByName(manageFeeds)

    def retranslateUi(self, manageFeeds):
        manageFeeds.setWindowTitle(QtGui.QApplication.translate("manageFeeds", "Manage Feeds", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("manageFeeds", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("manageFeeds", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("manageFeeds", "E&xit", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
