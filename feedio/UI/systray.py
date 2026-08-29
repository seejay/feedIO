import sys
from PyQt6 import QtWidgets, QtGui, QtCore
import threading

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent=None, child=None):
        # System tray icon requires the window to be controled passed as the child.
        super().__init__(icon, parent)
        menu = QtWidgets.QMenu(parent)
        self.updateAction = menu.addAction("&Update feeds")
        self.ConfigAction = menu.addAction("&Configure feedIO")
        self.reCalculateAction = menu.addAction("&ReCalculate Scores")
        self.minimizeAction = menu.addAction("Mi&nimize to tray")
        self.quitAction = menu.addAction("&Quit")
        self.setContextMenu(menu)
        self.parent = parent
        self.child = child

        self.quitAction.triggered.connect(parent.close)
        self.updateAction.triggered.connect(parent.fetchAllFeeds)
        self.reCalculateAction.triggered.connect(self.reCalculateAllScores)
        self.activated.connect(self.sysTrayActivated)
        self.minimizeAction.triggered.connect(child.hide)

    def sysTrayActivated(self, reason):
        """
        Function to handle the interactions with the system tray.
        """
        # reason = 3 when the system tray is clicked. Trigger is QSystemTrayIcon.ActivationReason.Trigger
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
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

    def reCalculateAllScores(self):
        """
        calls the parent.reCalculateAllScores inside a thread.
        """
        print("reCalculateAllScores called")
        thread = threading.Thread(target=self.parent.reCalculateAllScores, args=())
        thread.start()
