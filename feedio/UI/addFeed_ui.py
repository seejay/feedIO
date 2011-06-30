# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addFeed.ui'
#
# Created: Thu Jun 30 09:35:01 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_addFeed(object):
    def setupUi(self, addFeed):
        addFeed.setObjectName("addFeed")
        addFeed.resize(430, 166)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/feedIO.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        addFeed.setWindowIcon(icon)
        self.layoutWidget = QtGui.QWidget(addFeed)
        self.layoutWidget.setGeometry(QtCore.QRect(12, 13, 411, 151))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addFeedURLlabel = QtGui.QLabel(self.layoutWidget)
        self.addFeedURLlabel.setObjectName("addFeedURLlabel")
        self.horizontalLayout.addWidget(self.addFeedURLlabel)
        self.UrlLineEdit = QtGui.QLineEdit(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.UrlLineEdit.sizePolicy().hasHeightForWidth())
        self.UrlLineEdit.setSizePolicy(sizePolicy)
        self.UrlLineEdit.setInputMethodHints(QtCore.Qt.ImhUrlCharactersOnly)
        self.UrlLineEdit.setObjectName("UrlLineEdit")
        self.horizontalLayout.addWidget(self.UrlLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.addFeedTitleLabel = QtGui.QLabel(self.layoutWidget)
        self.addFeedTitleLabel.setEnabled(False)
        self.addFeedTitleLabel.setObjectName("addFeedTitleLabel")
        self.horizontalLayout_2.addWidget(self.addFeedTitleLabel)
        self.addFeedTitlelineEdit = QtGui.QLineEdit(self.layoutWidget)
        self.addFeedTitlelineEdit.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addFeedTitlelineEdit.sizePolicy().hasHeightForWidth())
        self.addFeedTitlelineEdit.setSizePolicy(sizePolicy)
        self.addFeedTitlelineEdit.setObjectName("addFeedTitlelineEdit")
        self.horizontalLayout_2.addWidget(self.addFeedTitlelineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.btnAdd = QtGui.QPushButton(self.layoutWidget)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout_3.addWidget(self.btnAdd)
        self.btnCancel = QtGui.QPushButton(self.layoutWidget)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_3.addWidget(self.btnCancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.retranslateUi(addFeed)
        QtCore.QMetaObject.connectSlotsByName(addFeed)

    def retranslateUi(self, addFeed):
        addFeed.setWindowTitle(QtGui.QApplication.translate("addFeed", "Add Feed", None, QtGui.QApplication.UnicodeUTF8))
        self.addFeedURLlabel.setText(QtGui.QApplication.translate("addFeed", "Feed URL", None, QtGui.QApplication.UnicodeUTF8))
        self.addFeedTitleLabel.setText(QtGui.QApplication.translate("addFeed", "Feed Title", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("addFeed", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("addFeed", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))

import feedIOicons_rc
