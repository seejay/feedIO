import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

class SystemTrayIcon(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None, child=None):
        # System tray icon requires the window to be controled passed as the child.
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        menu = QtGui.QMenu(parent)
        self.updateAction = menu.addAction("&Update feeds")
        self.ConfigAction = menu.addAction("&Configure feedIO")
        self.minimizeAction = menu.addAction("Mi&nimize to tray")
        self.quitAction = menu.addAction("&Quit")
        self.setContextMenu(menu)
        self.parent = parent
        self.child = child

        self.connect(self.quitAction, QtCore.SIGNAL("activated()"), parent.close)
        self.connect(self.updateAction, QtCore.SIGNAL("activated()"), child.fetchAllFeeds)
        self.connect(self, QtCore.SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self.sysTrayActivated)
        self.connect(self.minimizeAction, QtCore.SIGNAL("activated()"), child.hide)


    def sysTrayActivated(self, reason):
        """
        Function to handle the interactions with the system tray.
        """
        # reason = 3 when the system tray is clicked.
        if reason == 3:
            self.togalMainWindow()


    def togalMainWindow(self):
        """
        Togles the main window visibility.
        """
        if self.child.isVisible():
            self.child.hide()
        else:
            self.child.show()
            self.child.ui.listUnread.setFocus()

