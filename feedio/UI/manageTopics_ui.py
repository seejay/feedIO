# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manageTopics.ui'
#
# Created: Tue Jul  5 08:53:15 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_manageTopics(object):
    def setupUi(self, manageTopics):
        manageTopics.setObjectName("manageTopics")
        manageTopics.resize(392, 293)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        manageTopics.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(manageTopics)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.topicLine = QtGui.QLineEdit(manageTopics)
        self.topicLine.setObjectName("topicLine")
        self.verticalLayout_2.addWidget(self.topicLine)
        self.topicList = QtGui.QListWidget(manageTopics)
        self.topicList.setWhatsThis("")
        self.topicList.setResizeMode(QtGui.QListView.Adjust)
        self.topicList.setObjectName("topicList")
        self.verticalLayout_2.addWidget(self.topicList)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.line = QtGui.QFrame(manageTopics)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnAdd = QtGui.QPushButton(manageTopics)
        self.btnAdd.setObjectName("btnAdd")
        self.verticalLayout.addWidget(self.btnAdd)
        self.btnRemove = QtGui.QPushButton(manageTopics)
        self.btnRemove.setObjectName("btnRemove")
        self.verticalLayout.addWidget(self.btnRemove)
        spacerItem = QtGui.QSpacerItem(20, 148, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.btnExit = QtGui.QPushButton(manageTopics)
        self.btnExit.setObjectName("btnExit")
        self.verticalLayout.addWidget(self.btnExit)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(manageTopics)
        QtCore.QMetaObject.connectSlotsByName(manageTopics)

    def retranslateUi(self, manageTopics):
        manageTopics.setWindowTitle(QtGui.QApplication.translate("manageTopics", "Manage Topics", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("manageTopics", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("manageTopics", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExit.setText(QtGui.QApplication.translate("manageTopics", "Exit", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
