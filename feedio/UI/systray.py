import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtGui.QMenu(parent)
        self.updateAction = menu.addAction("&Update feeds")
        self.ConfigAction = menu.addAction("&Configure feedIO")
        self.quitAction = menu.addAction("&Quit")
        self.setContextMenu(menu)
        self.displayMain = True
        self.parent = parent
        
        self.connect(self.quitAction, QtCore.SIGNAL("activated()"), parent.close)
        self.connect(self.updateAction, QtCore.SIGNAL("activated()"), parent.fetchAllFeeds)        
        self.connect(self, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.sysTrayActivated)
#        self.connect(self.minimizeAction, QtCore.SIGNAL("activated()"), parent.hide)


    def sysTrayActivated(self, reason):
        if reason == 3:
            self.togalMainWindow()
            
    
    def togalMainWindow(self):
        if self.displayMain:
            self.parent.hide()
            self.displayMain = False
        else:
            self.parent.show()
            self.displayMain = True
            

