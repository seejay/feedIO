# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'removeFeed.ui'
#
# Created: Thu Jun 30 09:35:02 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_removeFeed(object):
    def setupUi(self, removeFeed):
        removeFeed.setObjectName("removeFeed")
        removeFeed.resize(422, 150)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        removeFeed.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(removeFeed)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.feedList = QtGui.QComboBox(removeFeed)
        self.feedList.setMinimumSize(QtCore.QSize(291, 0))
        self.feedList.setObjectName("feedList")
        self.verticalLayout.addWidget(self.feedList)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnRemove = QtGui.QPushButton(removeFeed)
        self.btnRemove.setObjectName("btnRemove")
        self.horizontalLayout.addWidget(self.btnRemove)
        self.btnCancel = QtGui.QPushButton(removeFeed)
        self.btnCancel.setWhatsThis("")
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(removeFeed)
        QtCore.QMetaObject.connectSlotsByName(removeFeed)

    def retranslateUi(self, removeFeed):
        removeFeed.setWindowTitle(QtGui.QApplication.translate("removeFeed", "Remove Feed", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("removeFeed", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("removeFeed", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
