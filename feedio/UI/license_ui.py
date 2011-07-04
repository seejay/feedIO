# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'license.ui'
#
# Created: Mon Jul  4 22:05:03 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_License(object):
    def setupUi(self, License):
        License.setObjectName("License")
        License.resize(521, 316)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        License.setWindowIcon(icon)
        self.txtBrserLicense = QtGui.QTextBrowser(License)
        self.txtBrserLicense.setGeometry(QtCore.QRect(10, 10, 501, 251))
        self.txtBrserLicense.setObjectName("txtBrserLicense")
        self.btnClose = QtGui.QPushButton(License)
        self.btnClose.setGeometry(QtCore.QRect(395, 274, 91, 27))
        self.btnClose.setObjectName("btnClose")

        self.retranslateUi(License)
        QtCore.QMetaObject.connectSlotsByName(License)

    def retranslateUi(self, License):
        License.setWindowTitle(QtGui.QApplication.translate("License", "License", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("License", "&Close", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
