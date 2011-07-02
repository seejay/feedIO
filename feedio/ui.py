#!/usr/bin/python
"""
Author  : Chanaka Jayamal
Date    : 20/05/2011
GUI for the feedIO feed aggregator

"""

__version__ = "0.0.1"

__license__ = """
    Copyright (C) 2011 Sri Lanka Institute of Information Technology.

    feedIO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    feedIO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with feedIO.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Chanaka Jayamal <seejay@seejay.net>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Chamika Viraj"]


import sys
import time
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import threading
import time

from UI.feedIO_ui import Ui_feedIO
from UI.addFeed_ui import Ui_addFeed
from UI.manageFeeds_ui import Ui_manageFeeds
from UI.removeFeed_ui import Ui_removeFeed
from UI.addTopic_ui import Ui_addTopic
from UI.removeTopic_ui import Ui_removeTopic
from UI.manageTopics_ui import Ui_manageTopics
from UI.about_ui import Ui_About

from UI.systray import SystemTrayIcon
import feedmanager as fm

class mainUI(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_feedIO()
        self.ui.setupUi(self)
        self.raise_()

        self.feedList = []
        self.itemList = []
        self.displayFeeds()
        self.displayItems()

        self.connect(self.ui.comboFeed, SIGNAL("currentIndexChanged(int)"), self.displayItems)
        self.connect(self.ui.listUnread, SIGNAL("currentItemChanged(QListWidgetItem *,QListWidgetItem *)"), self.displayArticle)
        self.connect(self.ui.actionVisitPage, SIGNAL("activated()"), self.visitPage)
        self.connect(self.ui.actionFetchAllFeeds, SIGNAL("activated()"), self.fetchAllFeeds)
#        self.connect(self, SIGNAL('triggered()'), self.closeEvent)

    def closeEvent(self, event):
        """
        Modification to the closeEvent so that pressing the close button in main window will only exit the
        """
        self.hide()
        event.ignore()

    def displayFeeds(self):
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        feedTitles.append("All Feeds")
        self.ui.comboFeed.clear()
        self.ui.comboFeed.addItems(feedTitles)

    def displayItems(self):
        """
        function to update the Articles list according to the selected feeds list.
        """
        selectedIndex = self.ui.comboFeed.currentIndex()

        if len(self.feedList) == 0:
            itemTitles = []
        else:

            if selectedIndex == len(self.feedList):
                self.itemList = fm.listItems()
                itemTitles = [item.title for item in self.itemList]
                windowTitle = "All Feeds - feedIO"
                self.setWindowTitle(windowTitle)
            else:
                selectedFeed = self.feedList[selectedIndex]
                self.itemList = fm.listItems(selectedFeed)
                itemTitles = [item.title for item in self.itemList]
                #Code to change the window title to the currently viewing feed's title
                windowTitle = selectedFeed.title + " - feedIO"
                self.setWindowTitle(windowTitle)

        self.ui.listUnread.clear()
        self.ui.listUnread.addItems(itemTitles)

    def displayArticle(self):
        """
        displays the selected article on the viewer.
        """
        try:
            selectedItemIndex = self.ui.listUnread.currentRow()
            selectedItem = self.itemList[selectedItemIndex]
            text = "<font face=Georgia>" + "<H3>" + selectedItem.title + \
                "</H3>(" + selectedItem.feed.title + ")<br>" + \
                time.ctime(selectedItem.updated) + "<br>" + \
                selectedItem.description + "</font>"
        except:
            text = "Add some interesting feeds!"
        else:
            self.ui.viewArticle.setHtml(text)
            windowTitle = selectedItem.title + " - " + selectedItem.feed.title + " - feedIO"
            self.setWindowTitle(windowTitle)


    def fetchAllFeeds(self):
        """
        Fetch all action implementataion. Creates a new thread and fetches the updates for them in that thread.
        """

        thread = threading.Thread(target=fm.updateAll, args=())
        thread.start()


    def  visitPage(self):
        """
        function to visit the original web page of selected article from the built in web browser.
        """
        try:
            selectedItemIndex = self.ui.listUnread.currentRow()
            selectedItem = self.itemList[selectedItemIndex]
        except:
            text = "Not implemented yet."
        else:
            self.ui.viewArticle.load(QUrl(selectedItem.url))


    def on_actionManageFeeds_activated(self, i = None):
        """
        Manage feeds action implementataion. displays the manageFeeds dialog box.
        """
        if i is None: return
        ManageFeedsDialog(self).exec_()
        self.displayFeeds()


    def on_actionAddFeed_activated(self, i = None):
        if i is None: return

        AddFeedDialog(self).exec_()
        self.displayFeeds()

    def on_actionRemoveFeed_activated(self, i = None):
        if i is None: return

        RemoveFeedDialog(self).exec_()
        self.displayFeeds()


    def on_actionManageTopics_activated(self, i = None):
        """
        Manage feeds action implementataion. displays the manageFeeds dialog box.
        """
        if i is None: return

        ManageTopicsDialog(self).exec_()


    def on_actionAddTopic_activated(self, i = None):
        if i is None: return

        AddTopicDialog(self).exec_()


    def on_actionRemoveTopic_activated(self, i = None):
        if i is None: return

        RemoveTopicDialog(self).exec_()


    def on_actionExit_activated(self, i = None):
        """
        Exit action implementataion. Exits the application.
        """
        if i is None: return
        self.parent.close()

    def on_actionMinimizeToTray_activated(self, i = None):
        """
        Exit action implementataion. Exits the application.
        """
        if i is None: return
        self.close()
    
    def on_actionAbout_activated(self, i = None):
        """
        About action implementataion.
        """
        if i is None: return
        AboutDialog(self).exec_()


class AddFeedDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addFeed()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL("clicked()"), self.addFeed)
        self.connect(self.ui.UrlLineEdit, SIGNAL("returnPressed()"), self.addFeed)

    def addFeed(self):
        feedUrl = unicode(self.ui.UrlLineEdit.text())

        thread = threading.Thread(target=fm.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()
#        fm.addFeed(feedUrl)

        thread.join()
        self.close()


class RemoveFeedDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_removeFeed()
        self.ui.setupUi(self)
        self.feedList = []
        self.displayFeeds()

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL("clicked()"), self.removeFeed)

    def displayFeeds(self):
        """
        function to display the subscribed feeds list in the combo box.
        """
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        self.ui.feedList.clear()
        self.ui.feedList.addItems(feedTitles)

    def removeFeed(self):
        selectedIndex = self.ui.feedList.currentIndex()
        selectedFeed = self.feedList[selectedIndex]
        fm.removeFeed(selectedFeed)
        self.close()


class ManageFeedsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageFeeds()
        self.ui.setupUi(self)
        self.displayFeeds()

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))

    def displayFeeds(self):
        feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in feedList]
        self.ui.feedList.clear()
        self.ui.feedList.addItems(feedTitles)


class AddTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addTopic()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))


class RemoveTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_removeTopic()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))


class ManageTopicsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageTopics()
        self.ui.setupUi(self)

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))

class AboutDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_About()
        self.ui.setupUi(self)

def initUI():

    app = QApplication(sys.argv)
    #Splash screen implementation
    splash_pix = QPixmap(":/images/splash.png")
#    splash_pix = QPixmap('./images/feedIO-splash.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())

    splash.show()
    app.processEvents()

#    time.sleep(2)

    # create a feedIO QWidget instance
    feedIO = QWidget()

    # pass feedIO as the parent for the mainWindow.
    mainWindow = mainUI(feedIO)

    # system tray icon
    icon = QIcon()
    icon.addPixmap(QPixmap(":/images/feedIO.png"), QIcon.Normal, QIcon.Off)

    # Pass the feedIO instance as the parent and the mainWindow instance as the child.
    trayIcon = SystemTrayIcon(icon, feedIO, mainWindow)

    #tool tip for the system try icon.
    # TODO this should be updated appropriately at run time.
    trayIcon.setToolTip("feedIO " + __version__ + " developer build running...")
    trayIcon.show()

    mainWindow.show()
    splash.finish(mainWindow)
    sys.exit(app.exec_())


if __name__ == "__main__":
    initUI()
