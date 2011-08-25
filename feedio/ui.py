#!/usr/bin/python
"""
Author  : Chanaka Jayamal
Date    : 20/05/2011
GUI for the feedIO feed aggregator

"""

__version__ = "0.0.3"

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
from UI.twitterPIN_ui import Ui_twitterPIN
from UI.rilLogin_ui import Ui_rilLogin
from UI.about_ui import Ui_About
from UI.license_ui import Ui_License
from UI.credits_ui import Ui_Credits
from UI.settings_ui import Ui_settings

from UI.systray import SystemTrayIcon
import feedmanager as fm
import classifier
import prioritizer
import purify
import notifier
import twitterPlugin
import rilPlugin
import tweepy
import webbrowser
import speechengine


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
        self.readList = []
        self.currentItem = None
        self.currentTopic = classifier.getTopic("General")

        self.updated = True
        self.displayTopics()
        self.displayFeeds()
        self.displayItems()

        self.ui.listOld.setFocus()
        self.ui.comboFeed.setCurrentIndex(len(self.feedList))


        # Twitter authentication details.
#        self.twitterAuthenticated = False
#        self.twitterAuthKey = ''
#        self.twitterAuthSecret = ''

        self.connect(self.ui.comboFeed, SIGNAL("currentIndexChanged(int)"), self.displayItems)
        self.connect(self.ui.comboTopic, SIGNAL("currentIndexChanged(int)"), self.displayItems)
        self.connect(self.ui.listUnread, SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.setCurrentFromUnread)

        self.connect(self.ui.listUnread, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.on_actionReadItLater_activated)
        self.connect(self.ui.listOld, SIGNAL("itemDoubleClicked(QTreeWidgetItem *,int)"), self.on_actionReadItLater_activated)

        self.connect(self.ui.listOld, SIGNAL("currentItemChanged(QTreeWidgetItem *,QTreeWidgetItem *)"), self.setCurrentFromOld)
        self.connect(self.ui.actionVisitPage, SIGNAL("activated()"), self.visitPage)
        self.connect(self.ui.actionFetchAllFeeds, SIGNAL("activated()"), parent.fetchAllFeeds)
        self.connect(self.ui.actionReCalculateScores, SIGNAL("activated()"), self.reCalculateAllScores)
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
        Function to display unread and read article lists in the Two QTreeWidget
        boxes using two seperate threads to keep the UI responsiveness.
        """
        self.displayUnread()
        self.displayRead()


    def displayUnread(self):
        """
        function to update the Unread Articles list according to the selected feeds list.
        """

        selectedFeedIndex = self.ui.comboFeed.currentIndex()

        selectedTopicIndex = self.ui.comboTopic.currentIndex()
        self.currentTopic = self.topicList[selectedTopicIndex]
        print self.currentTopic

        if len(self.feedList) == 0:
            self.scoreItemList = []
        else:

            if selectedFeedIndex == len(self.feedList):
                pri = prioritizer.Prioritizer(self.currentTopic)
                self.scoreItemList = pri.listScoreItems()
                # Now filter out the Old items using a generator
                #this is being done in the prioritizer now
#                self.scoreItemList = [scoreItem for scoreItem in self.scoreItemList if scoreItem.item.isUnread is True]

                # prioritize the list according to the scores
                self.scoreItemList = pri.prioritize(self.scoreItemList)

                windowTitle = "All Feeds - feedIO"
                self.setWindowTitle(windowTitle)
            else:
                selectedFeed = self.feedList[selectedFeedIndex]

                pri = prioritizer.Prioritizer(self.currentTopic)
                self.scoreItemList = pri.listScoreItems(selectedFeed)
                # Now filter out the items for the current Feed using a generator
                #this is being done in the prioritizer now
#                self.scoreItemList = [scoreItem for scoreItem in self.scoreItemList if (scoreItem.item.feed is selectedFeed and scoreItem.item.isUnread is True)]

                self.scoreItemList = pri.prioritize(self.scoreItemList)

                #Code to change the window title to the currently viewing feed's title
                windowTitle = selectedFeed.title + " - feedIO"
                self.setWindowTitle(windowTitle)

        self.ui.listUnread.clear()

        itemIcon = QIcon()
        itemIcon.addPixmap(QPixmap(":/images/article.png"), QIcon.Normal, QIcon.Off)

        # Sort self.scoreItemList according to "isNew" property as primary
        # Secondary sort it by isUnread
        # Then sort it according to Score
        # then sort it according to the Article date.

        for scoreItem in self.scoreItemList:
#            treeItem=QTreeWidgetItem([ str(scoreItem.score), scoreItem.item.title])
            treeItem=QTreeWidgetItem([scoreItem.item.title,])
            treeItem.article = scoreItem.item

            treeItem.setIcon(0, itemIcon)

#            # Set a part of the article text as the tooltip of Items
#            itemTip = purify.cleanText(str(scoreItem.score))
            itemTip = "Score: <b>" + str(scoreItem.score) + "</b> &nbsp; &nbsp;&nbsp;" + "<br>Topic: " + "<i>" + scoreItem.topic.title + "</i>" + "<br>Via: " + "<i>" + scoreItem.item.feed.title + "</i>"
#            tip = purify.shorten(itemTip, 200)
            treeItem.setToolTip(0, itemTip)

            if scoreItem.item.age is 0:
                treeItem.setFont(0, self.newFont)
                treeItem.setTextColor(0, self.newColor)

            elif scoreItem.item.age is 1:
                treeItem.setFont(0, self.unreadFont)
                treeItem.setTextColor(0, self.unreadColor)

            else:
                treeItem.setFont(0, self.readFont)
                treeItem.setTextColor(0, self.readColor)

            self.ui.listUnread.addTopLevelItem(treeItem)

        self.ui.listOld.setFocus()


    def displayRead(self):
        """
        function to update the read Articles list according to the selected feeds list.
        """
        pass

        selectedFeedIndex = self.ui.comboFeed.currentIndex()

        if len(self.feedList) == 0:
            self.readList = []
        else:

            if selectedFeedIndex == len(self.feedList):
                self.readList = fm.listRead()

            else:
                selectedFeed = self.feedList[selectedFeedIndex]

                self.readList = fm.listRead(selectedFeed)

        self.ui.listOld.clear()

        itemIcon = QIcon()
        itemIcon.addPixmap(QPixmap(":/images/article.png"), QIcon.Normal, QIcon.Off)

        for article in self.readList:
            treeItem=QTreeWidgetItem([article.title,])
            treeItem.article = article

            treeItem.setIcon(0, itemIcon)

            treeItem.setFont(0, self.readFont)
            treeItem.setTextColor(0, self.readColor)

            self.ui.listOld.addTopLevelItem(treeItem)

    def setCurrentFromUnread(self):
        """
        Function to set the currently selected Item in the Unread list as the self.currentItem
        """
        self.currentItem = self.ui.listUnread.currentItem()
        self.displayArticle()


    def setCurrentFromOld(self):
        """
        Function to set the currently selected Item in the Old list as the self.currentItem
        """
        self.currentItem = self.ui.listOld.currentItem()
        self.displayArticle()


    def displayArticle(self):
        """
        displays the selected article on the viewer.
        """
        try:
            selected = self.currentItem
            selectedItem = selected.article

            text = "<style>.bg_color {background-color: #f8f8ff ;}.blue {color: #6f6fff;}.big { font-size: 8em; }.bold { font-weight: bold; }.date{ font-weight: bold; color: #066bb6;  }.info     { font-size: .95em; margin: 2px 0 6px !important; color: #148d04; }.headline_font_size {font-size: .80em;}</style>" + \
                "<div class=\" bg_color \">" + \
                "<div class=\" blue \">" + \
                "<H3>" + selectedItem.title + \
                "</div>" + \
                "<div class=\" bold headline_font_size\">" + \
                "</H3>(" + selectedItem.feed.title + ")<br>" + \
                "</div>" + \
                "<div class=\"date info\">" + \
                time.ctime(selectedItem.updated) + "<br>" + \
                "</div>" + \
                "<div class = \"bg_color\">" + \
                selectedItem.description + \
                "</div>"
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
        selected = self.currentItem
        selected.setFont(0, self.readFont)
        selected.setTextColor(0,self.readColor)
        fm.setItemFlag(selected.article, 2)


    def markAsUnread(self):
        # create font with heavy weight to show the unread articles
        selected = self.currentItem
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

        print "Calculating priority Scores"
        self.parent.setNewItemScores()


    def fetchFeed(self):
        """
        Fetch the selected feed.
        """
        selected = self.currentItem
        thread = threading.Thread(target=fm.updateFeed, args=(selected.article.feed,))
        thread.start()


    def  visitPage(self):
        """
        function to visit the original web page of selected article from the built in web browser.
        """
        try:
            selected = self.currentItem
        except:
            text = "Not implemented yet."
        else:
            self.ui.viewArticle.load(QUrl(selected.article.url))

            self.parent.status = "Visiting %s in browser mode..." % selected.article.feed.title
            self.parent.sendNotification()



    def upVoteArticle(self):
        """
        Function to upvote the current article
        """
        selected = self.currentItem

        if selected == None:
            print "Nothing to vote!"
        else:
            selectedTopicIndex = self.ui.comboTopic.currentIndex()
            selectedTopic = self.topicList[selectedTopicIndex]

            #call the classifier module
            classifier.voteArticle("up",selected.article, selectedTopic)

#            #upVote the feed
#            classifier.voteFeed("up", selected.article.feed)
#            print "Up Voted %s" % selected.article.title

            self.parent.status = "Up Voted %s under %s" % (selected.article.title, selectedTopic.title)
            self.parent.sendNotification()


    def downVoteArticle(self):
        """
        Function to Down Vote the current article
        """
        selected = self.currentItem

        if selected == None:
            print "Nothing to vote!"
        else:
            selectedTopicIndex = self.ui.comboTopic.currentIndex()
            selectedTopic = self.topicList[selectedTopicIndex]

            #call the classifier module
            classifier.voteArticle("down", selected.article, selectedTopic)

#            #downVote the feed
#            classifier.voteFeed("down", selected.article.feed)
#            print "Down Voted %s" % selected.article.title

            self.parent.status = "Down Voted %s under %s" % (selected.article.title, selectedTopic.title)
            self.parent.sendNotification()

    def reCalculateAllScores(self):
        """
        calls the parent.reCalculateAllScores inside a thread.
        """
        print "reCalculateAllScores called"
        thread = threading.Thread(target=self.parent.reCalculateAllScores, args=())
#        thread.setDaemon(True)
        thread.start()



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

    def on_actionRead_activated(self, i = None):
        """
        Read article implementataion.Can play or stop the selected article.
        """
        if i is None: return
        selected = self.currentItem
        if self.parent.playerState =='standby':
            self.parent.playerState = 'playing'
            self.parent.sp.say(purify.cleanText(str(selected.article.title + "....." + selected.article.description)))
            #self.sp.say(selected.article.description)
        	
        else:
            self.parent.sp.stop()
            self.parent.playerState='standby'

    def on_actionPreferences_activated(self, i = None):
        """
        Settings  action implementataion.
        """
        if i is None: return
        SettingsDialog(self).exec_()


    def on_actionSignInToTwitter_activated(self, i = None):
        """
        Sign into twitter.
        """
        if i is None: return

        # create a QSettings object to get twitter auth data.
        s = QSettings()
        twitterPlugin.ACCESS_KEY  = str(s.value("TWITTER_ACCESS_KEY").toString())
        twitterPlugin.ACCESS_SECRET = str(s.value("TWITTER_ACCESS_SECRET").toString())


        if twitterPlugin.ACCESS_KEY is '':
            try:
                print "signing into twitter using the browser..."
                tp = twitterPlugin.TwitterPlugin()

                auth_url = tp.authenticate()

                webbrowser.open_new(auth_url)

                TwitterPinDialog(self).exec_()
                # return is the VERIFIER code is not set.
                if twitterPlugin.VERIFIER is '': return

                (twitterPlugin.ACCESS_KEY, twitterPlugin.ACCESS_SECRET) = tp.verify()
                #Store the values using in a QSettings object.
                s = QSettings()

                s.setValue("TWITTER_ACCESS_KEY", twitterPlugin.ACCESS_KEY)
                s.setValue("TWITTER_ACCESS_SECRET", twitterPlugin.ACCESS_SECRET)


            except tweepy.TweepError:
                print "Not authenticated properly. check the PIN number"
                self.parent.status = "Error Logging to twitter.com!"
                self.parent.sendNotification()
            else:
                self.parent.status = "You have Signed in to twitter.com"
                self.parent.sendNotification()


    def on_actionSignOffFromTwitter_activated(self, i = None):
        """
        Sign off from the twitter session.
        """
        if i is None: return

        twitterPlugin.ACCESS_KEY = ''
        twitterPlugin.ACCESS_SECRET = ''
        twitterPlugin.VERIFIER = ''

        #Store the values using in a QSettings object.
        s = QSettings()

        s.setValue("TWITTER_ACCESS_KEY", twitterPlugin.ACCESS_KEY)
        s.setValue("TWITTER_ACCESS_SECRET", twitterPlugin.ACCESS_SECRET)

        self.parent.status = "You have Signed Off from twitter."
        self.parent.sendNotification()

        print "Signed off from twitter."


    def on_actionPostToTwitter_activated(self, i = None):
        """
        post to twitter action implementataion.
        """
        if i is None: return

        selected = self.currentItem
        shortUrl = purify.shortenUrl(selected.article.url)
        if shortUrl is False: return

#        # Dirty hack to make the tweet limit to 140 chars.
#        urlWidth = len(selected.article.url)
#        articleTitle = purify.shorten(selected.article.title, (135-urlWidth))

        message = selected.article.title +" "+ shortUrl

#        message = selected.article.url + selected.article.title

        # create a QSettings object to get twitter auth data.
        s = QSettings()
        twitterPlugin.ACCESS_KEY  = str(s.value("TWITTER_ACCESS_KEY").toString())
        twitterPlugin.ACCESS_SECRET = str(s.value("TWITTER_ACCESS_SECRET").toString())

        if twitterPlugin.ACCESS_KEY is '':
            try:
                print "signing into twitter using the browser..."
                tp = twitterPlugin.TwitterPlugin()

                auth_url = tp.authenticate()

                webbrowser.open_new(auth_url)

                TwitterPinDialog(self).exec_()
                # return is the VERIFIER code is not set.
                if twitterPlugin.VERIFIER is '': return

                (twitterPlugin.ACCESS_KEY, twitterPlugin.ACCESS_SECRET) = tp.verify()
                #Store the values using in a QSettings object.
                s = QSettings()
                s.setValue("TWITTER_ACCESS_KEY", twitterPlugin.ACCESS_KEY)
                s.setValue("TWITTER_ACCESS_SECRET", twitterPlugin.ACCESS_SECRET)

            except tweepy.TweepError:
                print "Not authenticated properly. check the PIN number"
                self.parent.status = "Error Logging to twitter.com!"
                self.parent.sendNotification()

            else:
                tp.tweet(message)
                self.parent.status = message + " posted to twitter."
                self.parent.sendNotification()

        else:
            try:
                tp = twitterPlugin.TwitterPlugin()
                tp.tweet(message)
            except:
                print "Error in tweeting"
            else:
                self.parent.status = message + " posted to twitter."
                self.parent.sendNotification()


    def on_actionSignInToRIL_activated(self, i = None):
        """
        Sign in to Read It Later, action implementataion.
        """
        if i is None: return
        rilPlugin.SESSION = None

        print "Asking to Sign into RIL..."
        RilLoginDialog(self).exec_()

        if rilPlugin.SESSION is None: return

        # TODO: do something like bookmarking the selected article.
        self.parent.status = "Signed in to Read It Later..."
        self.parent.sendNotification()


    def on_actionSignOffFromRIL_activated(self, i = None):
        """
        Sign off from Read It Later, action implementataion.
        """
        if i is None: return

        rilPlugin.SESSION = None
        # create a QSettings object to get RIL auth data.
        s = QSettings()
        s.setValue("RIL_USER", '')
        s.setValue("RIL_PW", '')

        self.parent.status = "You have Signed Off from Read It Later."
        self.parent.sendNotification()

        print "Signed off from RIL."


    def on_actionReadItLater_activated(self, i = None):
        """
        Read It Later, action implementataion.
        """
        if i is None: return

        selected = self.currentItem


        if rilPlugin.SESSION is None:
            s = QSettings()
            username = str(s.value("RIL_USER").toString())
            pw = str(s.value("RIL_PW").toString())

            if username is not '' and pw is not '':
                # Not logged in but the username and pw is there.
                try:
                    rilPlugin.SESSION = rilPlugin.RilSession(username, pw)
                    rilPlugin.SESSION.submitItem(selected.article)
                except rilPlugin.LogInError:
                    print "LoginError! invalid username/pw."
                    ## invalid credentials. prompt to re-enter username/pw.
                    #self.on_actionSignOffFromRIL_activated()
                else:
                    # TODO: do something like bookmarking the selected article.
                    self.parent.status = selected.article.title + "Added to Read It Later List."
                    self.parent.sendNotification()

            else:
                # Not logged in and the username and pw is not stored.
                print "Asking to Sign into RIL..."
                RilLoginDialog(self).exec_()

                if rilPlugin.SESSION is not None:
                    try:
                        rilPlugin.SESSION.submitItem(selected.article)
                    except:
                        print "Error in Submitting to RIL"
                    else:
                        # TODO: do something like bookmarking the selected article.
                        self.parent.status = selected.article.title + "Added to Read It Later List."
                        self.parent.sendNotification()

        else:
            try:
                rilPlugin.SESSION.submitItem(selected.article)
            except:
                print "Error in Submitting to RIL"
            else:
                # TODO: do something like bookmarking the selected article.
                self.parent.status = selected.article.title + "Added to Read It Later List."
                self.parent.sendNotification()


class AddFeedDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addFeed()
        self.ui.setupUi(self)
        self.parent = parent

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL("clicked()"), self.addFeed)
        self.connect(self.ui.UrlLineEdit, SIGNAL("returnPressed()"), self.addFeed)


    def addFeed(self):
        feedUrl = unicode(self.ui.UrlLineEdit.text())

        thread = threading.Thread(target=self.parent.parent.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()
        thread.join()

        if self.parent.parent.newFeed is True:
            itemList = fm.listNew()
            classifier.assignItemsToTopics(itemList)
            self.parent.parent.setNewItemScores()
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

        classifier.removefromScoreTable(selectedFeed)
        fm.removeFeed(selectedFeed)

        self.close()


class ManageFeedsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_manageFeeds()
        self.ui.setupUi(self)
        self.feedList = []
        self.displayFeeds()
        self.parent = parent

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
        classifier.removefromScoreTable(selectedFeed)
        fm.removeFeed(selectedFeed)
        self.displayFeeds()


    def addFeed(self):
        feedUrl = unicode(self.ui.urlLine.text())
        #Run the addFeed function in a new thread so that the ui is responsive.
        thread = threading.Thread(target=self.parent.parent.addFeed, args=(feedUrl,))
        thread.setDaemon(True)
        thread.start()
        thread.join()

        if self.parent.parent.newFeed is True:
            itemList = fm.listNew()
            classifier.assignItemsToTopics(itemList)
            self.parent.parent.setNewItemScores()

            self.ui.urlLine.clear()
            self.displayFeeds()


class AddTopicDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_addTopic()
        self.ui.setupUi(self)
        self.parent = parent

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnAdd, SIGNAL('clicked()'), self.addTopic)

    def addTopic(self):
        topic = unicode(self.ui.addTopicLinedit.text())
        #topic = purify.cleanText(topic) # gave an error when adding
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


class TwitterPinDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_twitterPIN()
        self.ui.setupUi(self)
        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnOK, SIGNAL('clicked()'), self.getPin)

    def getPin(self):
        twitterPlugin.VERIFIER = self.ui.pinLineEdit.text()
        self.close()


class RilLoginDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui = Ui_rilLogin()
        self.ui.setupUi(self)
        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnOk, SIGNAL('clicked()'), self.login)
        self.connect(self.ui.passwordLineEdit, SIGNAL("returnPressed()"), self.login)
        self.connect(self.ui.userNameLineEdit, SIGNAL("returnPressed()"), self.login)

    def login(self):
        """
        """
        username = self.ui.userNameLineEdit.text()
        password = self.ui.passwordLineEdit.text()

        try:
             rilPlugin.SESSION = rilPlugin.RilSession(username, password)
        except rilPlugin.LogInError:
            self.ui.lblStatus.setText("Invalid username/password!. Please retry.")
            print "LoginError! invalid username/password."

        else:
            if self.ui.chkKeepSigned.isChecked():
                #Store the username and PW for RIL
                s = QSettings()
                s.setValue("RIL_USER", username)
                s.setValue("RIL_PW", password)

            self.close()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.ui=Ui_settings()
        self.ui.setupUi(self)

        self.connect(self.ui.btnCancel, SIGNAL('clicked()'), SLOT('close()'))
        self.connect(self.ui.btnSave, SIGNAL("clicked()"), SLOT('close()'))


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

        self.status = "Running..."

        #espeak speech engine initiation
        self.playerState='standby'
        self.sp=speechengine.SpeechEngine("40","150")

        self.newFeed = False

        self.updateInterval = 1800000 # time in miliseconds (30 minutes)

        timer = QTimer(self) # timer to fetch feeds automatically
        self.connect(timer, SIGNAL('timeout()'), self.fetchAllFeeds)
        timer.start(self.updateInterval)


    def sendNotification(self, title = "feedIO"):
        no = notifier.Notifier(title, self.status)
        no.feedNotification()


    def addFeed(self, feedUrl):
        try:
            fm.addFeed(feedUrl)
        except:
            self.status = "Error adding feed!"
            print self.status
            self.sendNotification()
        else:
            self.newFeed = True


    def fetchAllFeeds(self):
        thread = threading.Thread(target=self.fetchAll, args=())
        thread.start()

##    def calAllScores(self):
##        itemList = fm.listNew()
##        itemList.extend(fm.listUnread())
##        self.calcScores(itemList)

#    def calcScores(self, articleList):
#        pass
##        pri = prioritizer.Prioritizer()
##        pri.setScores(articleList)


    def fetchAll(self):
        self.status = "fetching Updates..."
        self.sendNotification()
        fm.updateAll()

        #assign the newly fetched articles to the topics
        newList = fm.listNew()
        classifier.assignItemsToTopics(newList)
        print "Assigned the new articles to topics"
        #calculate the priority scores of the new articles for each topic.
        self.setNewItemScores()

        self.status = "All feeds updated."
        print self.status
        self.sendNotification()


    def setNewItemScores(self):
        """
        Function to get the New Articles and calculate their scores under all the topics
        """
        #get all the topics
        topicsList = classifier.listTopics()

        for topic in topicsList:
            pri = prioritizer.Prioritizer(topic)
            scoreItemsList = pri.listScoreItems()
            scoreItemList = [scoreItem for scoreItem in scoreItemsList if scoreItem.item.age is 0]
            pri.setScores(scoreItemList)
            print "calculated New article scores for %s" % topic.title

    def reCalculateAllScores(self):
        """
        Function to get all the Unread Articles and calculate their scores under all the topics.
        """
        #get all the topics
        print "reCalculating All Scores"
        topicsList = classifier.listTopics()

        for topic in topicsList:
            self.reCalculateScores(topic)


    def reCalculateScores(self, topic):
        """
        Function to get all the Unread Articles and calculate their scores under the given topic.
        """
        print "calculating New article scores for %s" % topic.title
        pri = prioritizer.Prioritizer(topic)
        scoreItemsList = pri.listScoreItems()
#        scoreItemList = [scoreItem for scoreItem in scoreItemsList if scoreItem.item.isUnread is True]
        pri.setScores(scoreItemsList)
        print "calculated New article scores for %s" % topic.title
        self.status = "Calculated New article scores for %s" % topic.title
        self.sendNotification()



    def closeEvent(self, event):
        print "marking all new Items as old before exit"
        newItems = fm.listNew()
        for item in newItems:
            fm.setItemFlag(item, 1, False)
            print "marked %s new to unread" % item.title

        #check whether text to speech is still working
        if (self.playerState == 'playing'):
            self.sp.stop()
            self.playerState='standby'
            print "speech engine terminated on exit"
        else:
            pass

        # Might need to move this commit to a better place.
        # this is done to ruduce the number of commites to be performed when exiting, to one
        fm.session.commit()
        event.accept()


def initUI():

    app = QApplication(sys.argv)

    # Set up the Organization, Domain and App names to be used for QSettings.
    app.setOrganizationName("feedIO project")
    app.setOrganizationDomain("feedio.org")
    app.setApplicationName("feedIO")


#    #add following 3 lines to enable sinhala
#    translator = QTranslator(app)
#    translator.load("UI/feedio_sinhala")
#    app.installTranslator(translator)

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

