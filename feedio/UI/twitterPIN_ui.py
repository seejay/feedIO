# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'twitterPIN.ui'
#
# Created: Sat Aug  6 01:28:10 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_twitterPIN(object):
    def setupUi(self, twitterPIN):
        twitterPIN.setObjectName(_fromUtf8("twitterPIN"))
        self.gridLayout = QtGui.QGridLayout(twitterPIN)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(383, 24, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(twitterPIN)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pinLineEdit = QtGui.QLineEdit(twitterPIN)
        self.pinLineEdit.setObjectName(_fromUtf8("pinLineEdit"))
        self.horizontalLayout.addWidget(self.pinLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem2 = QtGui.QSpacerItem(381, 25, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btnCancel = QtGui.QPushButton(twitterPIN)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.btnOK = QtGui.QPushButton(twitterPIN)
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.horizontalLayout_2.addWidget(self.btnOK)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(twitterPIN)
        QtCore.QMetaObject.connectSlotsByName(twitterPIN)

    def retranslateUi(self, twitterPIN):
        twitterPIN.setWindowTitle(QtGui.QApplication.translate("twitterPIN", "twitter Auth Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("twitterPIN", "Twitter Authentication PIN :", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("twitterPIN", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOK.setText(QtGui.QApplication.translate("twitterPIN", "&OK", None, QtGui.QApplication.UnicodeUTF8))

