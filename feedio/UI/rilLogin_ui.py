# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rilLogin.ui'
#
# Created: Mon Aug 15 00:39:54 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_rilLogin(object):
    def setupUi(self, rilLogin):
        rilLogin.setObjectName(_fromUtf8("rilLogin"))
        rilLogin.resize(344, 172)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/feedIO.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        rilLogin.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(rilLogin)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblStatus = QtGui.QLabel(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.lblStatus.setFont(font)
        self.lblStatus.setObjectName(_fromUtf8("lblStatus"))
        self.gridLayout.addWidget(self.lblStatus, 0, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.userNameLineEdit = QtGui.QLineEdit(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.userNameLineEdit.setFont(font)
        self.userNameLineEdit.setObjectName(_fromUtf8("userNameLineEdit"))
        self.horizontalLayout.addWidget(self.userNameLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.passwordLineEdit = QtGui.QLineEdit(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.passwordLineEdit.setFont(font)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineEdit.setObjectName(_fromUtf8("passwordLineEdit"))
        self.horizontalLayout_2.addWidget(self.passwordLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.chkKeepSigned = QtGui.QCheckBox(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.chkKeepSigned.setFont(font)
        self.chkKeepSigned.setObjectName(_fromUtf8("chkKeepSigned"))
        self.horizontalLayout_4.addWidget(self.chkKeepSigned)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btnCancel = QtGui.QPushButton(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.btnCancel.setFont(font)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.horizontalLayout_3.addWidget(self.btnCancel)
        self.btnOk = QtGui.QPushButton(rilLogin)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        self.btnOk.setFont(font)
        self.btnOk.setObjectName(_fromUtf8("btnOk"))
        self.horizontalLayout_3.addWidget(self.btnOk)
        self.gridLayout.addLayout(self.horizontalLayout_3, 5, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 1, 0, 1, 1)

        self.retranslateUi(rilLogin)
        QtCore.QMetaObject.connectSlotsByName(rilLogin)
        rilLogin.setTabOrder(self.userNameLineEdit, self.passwordLineEdit)
        rilLogin.setTabOrder(self.passwordLineEdit, self.btnOk)
        rilLogin.setTabOrder(self.btnOk, self.btnCancel)
        rilLogin.setTabOrder(self.btnCancel, self.chkKeepSigned)

    def retranslateUi(self, rilLogin):
        rilLogin.setWindowTitle(QtGui.QApplication.translate("rilLogin", "Log in to Read It Later.", None, QtGui.QApplication.UnicodeUTF8))
        self.lblStatus.setText(QtGui.QApplication.translate("rilLogin", "Please Enter your Read It Later Username & Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("rilLogin", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("rilLogin", "Password: ", None, QtGui.QApplication.UnicodeUTF8))
        self.chkKeepSigned.setText(QtGui.QApplication.translate("rilLogin", "Keep  me &Signed In.", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("rilLogin", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOk.setText(QtGui.QApplication.translate("rilLogin", "&Ok", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
