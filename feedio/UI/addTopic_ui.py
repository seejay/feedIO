# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addTopic.ui'
#
# Created: Thu Jun 30 01:38:37 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_addTopic(object):
    def setupUi(self, addTopic):
        addTopic.setObjectName("addTopic")
        addTopic.setWindowModality(QtCore.Qt.NonModal)
        addTopic.resize(428, 155)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(addTopic.sizePolicy().hasHeightForWidth())
        addTopic.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setStrikeOut(False)
        addTopic.setFont(font)
        addTopic.setCursor(QtCore.Qt.ArrowCursor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        addTopic.setWindowIcon(icon)
        addTopic.setWindowOpacity(1.0)
        addTopic.setAutoFillBackground(False)
        self.gridLayout = QtGui.QGridLayout(addTopic)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(addTopic)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.addTopicLinedit = QtGui.QLineEdit(addTopic)
        self.addTopicLinedit.setMouseTracking(True)
        self.addTopicLinedit.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.addTopicLinedit.setAutoFillBackground(True)
        self.addTopicLinedit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.addTopicLinedit.setText("")
        self.addTopicLinedit.setEchoMode(QtGui.QLineEdit.Normal)
        self.addTopicLinedit.setCursorPosition(0)
        self.addTopicLinedit.setDragEnabled(False)
        self.addTopicLinedit.setObjectName("addTopicLinedit")
        self.horizontalLayout.addWidget(self.addTopicLinedit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(28, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnAdd = QtGui.QPushButton(addTopic)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout_2.addWidget(self.btnAdd)
        self.btnCancel = QtGui.QPushButton(addTopic)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.label.setBuddy(self.addTopicLinedit)

        self.retranslateUi(addTopic)
        QtCore.QMetaObject.connectSlotsByName(addTopic)

    def retranslateUi(self, addTopic):
        addTopic.setWindowTitle(QtGui.QApplication.translate("addTopic", "Add Topic", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("addTopic", "Topic", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("addTopic", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("addTopic", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
