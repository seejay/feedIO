# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'credits.ui'
#
# Created: Mon Jul  4 22:23:11 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Credits(object):
    def setupUi(self, Credits):
        Credits.setObjectName("Credits")
        Credits.resize(393, 283)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Credits.setWindowIcon(icon)
        self.tabCredits = QtGui.QTabWidget(Credits)
        self.tabCredits.setGeometry(QtCore.QRect(10, 20, 371, 211))
        self.tabCredits.setObjectName("tabCredits")
        self.Writtenby = QtGui.QWidget()
        self.Writtenby.setObjectName("Writtenby")
        self.tabCredits.addTab(self.Writtenby, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabCredits.addTab(self.tab_3, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabCredits.addTab(self.tab_2, "")
        self.btnClose = QtGui.QPushButton(Credits)
        self.btnClose.setGeometry(QtCore.QRect(280, 250, 91, 27))
        self.btnClose.setObjectName("btnClose")

        self.retranslateUi(Credits)
        self.tabCredits.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Credits)

    def retranslateUi(self, Credits):
        Credits.setWindowTitle(QtGui.QApplication.translate("Credits", "Credits", None, QtGui.QApplication.UnicodeUTF8))
        self.tabCredits.setTabText(self.tabCredits.indexOf(self.Writtenby), QtGui.QApplication.translate("Credits", "Written by", None, QtGui.QApplication.UnicodeUTF8))
        self.tabCredits.setTabText(self.tabCredits.indexOf(self.tab_3), QtGui.QApplication.translate("Credits", "Documented by", None, QtGui.QApplication.UnicodeUTF8))
        self.tabCredits.setTabText(self.tabCredits.indexOf(self.tab_2), QtGui.QApplication.translate("Credits", "At work by", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("Credits", "&Close", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
