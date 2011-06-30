# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'removeTopic.ui'
#
# Created: Thu Jun 30 09:35:02 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_removeTopic(object):
    def setupUi(self, removeTopic):
        removeTopic.setObjectName("removeTopic")
        removeTopic.resize(422, 150)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        removeTopic.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(removeTopic)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboBox = QtGui.QComboBox(removeTopic)
        self.comboBox.setMinimumSize(QtCore.QSize(291, 0))
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnRemove = QtGui.QPushButton(removeTopic)
        self.btnRemove.setObjectName("btnRemove")
        self.horizontalLayout.addWidget(self.btnRemove)
        self.btnCancel = QtGui.QPushButton(removeTopic)
        self.btnCancel.setWhatsThis("")
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout.addWidget(self.btnCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(removeTopic)
        QtCore.QMetaObject.connectSlotsByName(removeTopic)

    def retranslateUi(self, removeTopic):
        removeTopic.setWindowTitle(QtGui.QApplication.translate("removeTopic", "Remove Topic", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRemove.setText(QtGui.QApplication.translate("removeTopic", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("removeTopic", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
