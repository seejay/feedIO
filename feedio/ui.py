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
from UI.license_ui import Ui_License
from UI.credits_ui import Ui_Credits

from UI.systray import SystemTrayIcon
import feedmanager as fm
import classifier
import prioritizer
import purify

class mainUI(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_feedIO()
        self.ui.setupUi(self)
        self.raise_()

        self.newFont = QFont()
        self.newFont.setWeight(75)

        self.unreadFont = QFont()
        self.unreadFont.setWeight(75)

        self.readFont = QFont()
        self.readFont.setWeight(50)

        self.readColor = QColor("#666666")
        self.unreadColor = QColor("#444444")
        self.newColor = QColor("#070788")

        self.feedList = []
        self.itemList = []
        self.topicList = []
        self.updated = True
        self.displayTopics()
        self.displayFeeds()
        self.displayItems()

        self.ui.listUnread.setFocus()
        self.ui.comboFeed.setCurrentIndex(len(self.feedList))

        self.connect(self.ui.comboFeed, SIGNAL("currentIndexChanged(int)"), self.displayItems)
        self.connect(self.ui.listUnread, SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.displayArticle)
        self.connect(self.ui.actionVisitPage, SIGNAL("activated()"), self.visitPage)
        self.connect(self.ui.actionFetchAllFeeds, SIGNAL("activated()"), self.fetchAllFeeds)
        self.connect(self.ui.actionFetchFeed, SIGNAL("activated()"), self.fetchFeed)
        self.connect(self.ui.actionUpVote, SIGNAL("activated()"), self.upVoteArticle)
        self.connect(self.ui.actionDownVote, SIGNAL("activated()"), self.downVoteArticle)
        self.connect(self.ui.actionUnread, SIGNAL("activated()"), self.markAsUnread)
#        self.connect(self, SIGNAL('triggered()'), self.closeEvent)
        self.connect(self.ui.btnUp, SIGNAL('clicked()'), self.upVoteArticle)
        self.connect(self.ui.btnDown, SIGNAL('clicked()'), self.downVoteArticle)


    def closeEvent(self, event):
        """
        Modification to the closeEvent so that pressing the close button in main window will only exit the
        """
        self.hide()
        event.ignore()


    def displayTopics(self):
        self.topicList = classifier.listTopics()
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.comboTopic.clear()
        self.ui.comboTopic.addItems(topicTitles)


    def displayFeeds(self):
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        feedTitles.append("All Feeds")
        self.ui.comboFeed.clear()
        self.ui.comboFeed.addItems(feedTitles)
        self.ui.comboFeed.setCurrentIndex(len(self.feedList))


    def displayItems(self):
        """
        function to update the Articles list according to the selected feeds list.
        """

        selectedFeedIndex = self.ui.comboFeed.currentIndex()

        if len(self.feedList) == 0:
            self.itemList = []
        else:

            if selectedFeedIndex == len(self.feedList):
                self.itemList = fm.listNew()
                self.itemList.extend(fm.listUnread())
                pri = prioritizer.Prioritizer()

                self.itemList = pri.prioritize(self.itemList)

                windowTitle = "All Feeds - feedIO"
                self.setWindowTitle(windowTitle)
            else:
                selectedFeed = self.feedList[selectedFeedIndex]

                self.itemList = fm.listNew(selectedFeed)
                self.itemList.extend(fm.listUnread(selectedFeed))
                pri = prioritizer.Prioritizer()

                self.itemList = pri.prioritize(self.itemList)

                #Code to change the window title to the currently viewing feed's title
                windowTitle = selectedFeed.title + " - feedIO"
                self.setWindowTitle(windowTitle)

        self.ui.listUnread.clear()

        itemIcon = QIcon()
        itemIcon.addPixmap(QPixmap(":/images/article.png"), QIcon.Normal, QIcon.Off)

        # Sort self.itemList according to "isNew" property as primary
        # Secondary sort it by isUnread
        # Then sort it according to Score
        # then sort it according to the Article date.

        for article in self.itemList:
#            item=QTreeWidgetItem([article.title, str(time.ctime(article.updated))])
            item=QTreeWidgetItem([article.title,])
            item.article = article

            item.setIcon(0, itemIcon)

#            # Set a part of the article text as the tooltip of Items
#            tipLong = purify.cleanText(item.article.description)
#            tip = purify.shorten(tipLong, 200)
#            item.setToolTip(0, tip)

            if article.age is 0:
                item.setFont(0, self.newFont)
                item.setTextColor(0, self.newColor)

            elif article.age is 1:
                item.setFont(0, self.unreadFont)
                item.setTextColor(0, self.unreadColor)

            else:
                item.setFont(0, self.readFont)
                item.setTextColor(0, self.readColor)

            self.ui.listUnread.addTopLevelItem(item)

        self.ui.listUnread.setFocus()


    def displayArticle(self):
        """
        displays the selected article on the viewer.
        """
        try:
            selected = self.ui.listUnread.currentItem()
            selectedItem = selected.article

            text = "<font face=Georgia color =#444444 >" + "<H3>" + selectedItem.title + \
                "</H3>(" + selectedItem.feed.title + ")<br>" + \
                time.ctime(selectedItem.updated) + "<br>" + \
                selectedItem.description + "</font>"
        except:
            text = "Add some interesting feeds!"
        else:
            self.ui.viewArticle.setHtml(text)
            windowTitle = selectedItem.title + " - " + selectedItem.feed.title + " - feedIO"
            self.setWindowTitle(windowTitle)

            if selectedItem.age == 0 or selectedItem.age == 1:
                selected.setFont(0, self.readFont)
                selected.setTextColor(0, self.readColor)
                fm.setItemFlag(selectedItem, 2)


    def markAsRead(self):
        # create font with normal weight to show the read articles
        selected = self.ui.listUnread.currentItem()
        selected.setFont(0, self.readFont)
        selected.setTextColor(0,self.readColor)
        fm.setItemFlag(selected.article, 2)


    def markAsUnread(self):
        # create font with heavy weight to show the unread articles
        selected = self.ui.listUnread.currentItem()
        selected.setFont(0, self.unreadFont)
        selected.setTextColor(0, self.unreadColor)
        fm.setItemFlag(selected.article, 1)


    def fetchAllFeeds(self):
        """
        Fetch all action implementataion. Creates a new thread and fetches the updates for them in that thread.
        """

        thread = threading.Thread(target=self.fetchAll, args=())
        thread.start()
#        thread.join()
#        self.displayItems()

    def fetchAll(self):
        print "fetching Updates..."
        fm.updateAll()
        newList = fm.listNew()
        print "Calculating priority Scores"
        pri = prioritizer.Prioritizer()
        pri.setScores(newList)
        print "Done!"


    def fetchFeed(self):
        """
        Fetch the selected feed.
        """
        selected = self.ui.listUnread.currentItem()
        thread = threading.Thread(target=fm.updateFeed, args=(selected.article.feed,))
        thread.start()


    def  visitPage(self):
        """
        function to visit the original web page of selected article from the built in web browser.
        """
        try:
            selected = self.ui.listUnread.currentItem()
        except:
            text = "Not implemented yet."
        else:
            self.ui.viewArticle.load(QUrl(selected.article.url))


    def upVoteArticle(self):
        """
        Function to upvote the current article
        """
        selected = self.ui.listUnread.currentItem()

        if selected == None:
            print "Nothing to vote!"
        else:
            selectedTopicIndex = self.ui.comboTopic.currentIndex()
            selectedTopic = self.topicList[selectedTopicIndex]

            #call the classifier module
            classifier.voteArticle("up",selected.article)

            #upVote the feed
            classifier.voteFeed("up", selected.article.feed)
            print "Up Voted %s" % selected.article.title


    def downVoteArticle(self):
        """
        Function to Down Vote the current article
        """
        selected = self.ui.listUnread.currentItem()

        if selected == None:
            print "Nothing to vote!"
        else:
            selectedTopicIndex = self.ui.comboTopic.currentIndex()
            selectedTopic = self.topicList[selectedTopicIndex]

            #call the classifier module
            classifier.voteArticle("down", selected.article)

            #downVote the feed
            classifier.voteFeed("down", selected.article.feed)
            print "Down Voted %s" % selected.article.title


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
        self.displayTopics()


    def on_actionAddTopic_activated(self, i = None):
        if i is None: return

        AddTopicDialog(self).exec_()
        self.displayTopics()


    def on_actionRemoveTopic_activated(self, i = None):
        if i is None: return

        RemoveTopicDialog(self).exec_()
        self.displayTopics()


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
        self.feedList = []
        self.displayFeeds()

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL('clicked()'), self.removeFeed)
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addFeed)


    def displayFeeds(self):
        self.feedList = fm.listFeeds()
        feedTitles = [feed.title for feed in self.feedList]
        self.ui.feedList.clear()
        self.ui.feedList.addItems(feedTitles)


    def removeFeed(self):
        selectedItemIndex = self.ui.feedList.currentRow()
        selectedFeed = self.feedList[selectedItemIndex]
        fm.removeFeed(selectedFeed)
        self.displayFeeds()


    def addFeed(self):
        feedUrl = unicode(self.ui.urlLine.text())
        #Run the addFeed function in a new thread so that the ui is responsive.
        thread = threading.Thread(target=fm.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()
        thread.join()
        self.ui.urlLine.clear()
        self.displayFeeds()


class AddTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addTopic()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addTopic)

    def addTopic(self):
        topic = unicode(self.ui.addTopicLinedit.text())
        classifier.addTopic(topic)
        self.close()


class RemoveTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_removeTopic()
        self.ui.setupUi(self)

        self.topicList = []
        self.displayTopics()

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL("clicked()"), self.removeTopic)


    def displayTopics(self):
        """
        function to display the current topics list in the combo box.
        """
        self.topicList = classifier.listTopics()
        self.topicList.remove(classifier.getTopic("General"))
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.topicListCombo.clear()
        self.ui.topicListCombo.addItems(topicTitles)


    def removeTopic(self):
        selectedIndex = self.ui.topicListCombo.currentIndex()
        selectedTopic = self.topicList[selectedIndex]
        classifier.removeTopic(selectedTopic)
        self.close()


class ManageTopicsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageTopics()
        self.ui.setupUi(self)
        self.topicList = []
        self.displayTopics()

        self.connect(self.ui.btnExit, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnRemove, SIGNAL('clicked()'), self.removeTopic)
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addTopic)


    def displayTopics(self):
        self.topicList = classifier.listTopics()
        self.topicList.remove(classifier.getTopic("General"))
        topicTitles = [topic.title for topic in self.topicList]
        self.ui.topicList.clear()
        self.ui.topicList.addItems(topicTitles)


    def removeTopic(self):
        selectedItemIndex = self.ui.topicList.currentRow()
        selectedTopic = self.topicList[selectedItemIndex]
        classifier.removeTopic(selectedTopic)
        self.displayTopics()


    def addTopic(self):
        topic = unicode(self.ui.topicLine.text())
        classifier.addTopic(topic)
        self.ui.topicLine.clear()
        self.displayTopics()


class AboutDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_About()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnLicense, SIGNAL('clicked()'), self.loadLicense)
        self.connect(self.ui.btnCredits, SIGNAL('clicked()'), self.loadCredits)


    def loadLicense(self):
        LicenseDialog(self).exec_()


    def loadCredits(self):
        CreditsDialog(self).exec_()


class LicenseDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_License()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))


class CreditsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_Credits()
        self.ui.setupUi(self)

        self.connect(self.ui.btnClose, SIGNAL('clicked()'), SLOT('close()'))



class FeedIO(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        print "FeedIO instance created"

        self.updateInterval = 1800000 # time in miliseconds (30 minutes)

        timer = QTimer(self) # timer to fetch feeds automatically
        self.connect(timer, SIGNAL('timeout()'), self.fetchAllFeeds)
        timer.start(self.updateInterval)


    def fetchAllFeeds(self):
        print "fetching Updates..."
        fm.updateAll()
        newList = fm.listNew()
        pri = prioritizer.Prioritizer()
        pri.setScores(newList)


    def closeEvent(self, event):
        print "marking all new Items as old before exit"
        newItems = fm.listNew()
        for item in newItems:
            fm.setItemFlag(item, 1, False)
            print "marked %s new to unread" % item.title

        # Might need to move this commit to a better place.
        # this is done to ruduce the number of commites to be performed when exiting, to one
        fm.session.commit()
        event.accept()


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
    feedIO = FeedIO()

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
