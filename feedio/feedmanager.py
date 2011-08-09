#!/usr/bin/python
"""
feedManager for feedIO. provides functionality to add, remove and fetch updates
 from feeds.
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
import os
import time
from lib import feedparser
from models import *
from lib import autorss


USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
DBFILE=os.path.join(USERDIR,"feedIO.sqlite")


class FeedIOError(Exception): pass
class FeedError(FeedIOError): pass


def addFeed(feedUrl):
    """
    Function to add a new feed to the database.
    """
    try:
        feedUrl = autorss.getRSSLink(feedUrl)
        feedData = feedparser.parse(feedUrl)
    except:
        #this never occurs since parser does not raise any exceptions when invalid url is sent
        print "Invalid feed Url!"
        #raise FeedError

    else:
        try:
            newFeed = Feed(url = unicode(feedUrl), title = feedData.feed.title,
                lastModified = time.mktime(feedData.modified),
                etag = unicode(feedData.etag))

            session.commit()

        except AttributeError:
            session.rollback()
            print "Error! Invalid feed URL"
        except:
            session.rollback()
            print "%s \t Feed already subscribed" % (feedData.feed.title)

        else:
            try:
                # Get the topics list and assign the feed to all the available topics.
                topicsList = Topic.query.all()
                for topic in topicsList:
                    setFeedTopic(newFeed, topic, False)
                session.commit()
                print "Added %s to all topics" % newFeed.title
            except:
                session.rollback()
                print "Error setting up topics to the Feed"

            print "Subscribed to \t %s " % (feedData.feed.title)
            fetchFeeds(newFeed, feedData)
            topicsList = Topic.query.all()


def setFeedTopic(feed, topic, commit=True):
    """
    Assigns a feed to the given Topic.
    """
    if feed.topics.count(topic) == 0:
        feed.topics.append(topic)
        print "Added %s to %s" % (topic.title, feed.title)

        if commit is True:
            try:
                session.commit() # disable individual commits to increse performance.
            except:
                session.rollback()
                print "Error in setItemTopic"
                return None


def fetchFeeds(feed,feedData):
    for item in feedData.entries:
        _addItem(feed, item)


def _addItem(feed, item):
    """
    Function _addItem, adds a new article to the database.
    """
    try:
        newItem = Item(title = item.title,
            url = item.link,
            description = item.summary, feed = feed,
            updated = time.mktime(item.updated_parsed))

        session.commit()
    except:
        session.rollback()
        print " %s \t already exists" % (item.title)

def removeFeed(feed):
    """
    Function to remove a subscribed feed from the database.
    """
    try:

        itemList = listItems(feed)

        for item in itemList:
            print "deleted %s" % item.title
            _removeItem(item)

        # First delete all the scoreFeeds from the ScoreFeed table
        scoreFeeds = ScoreFeed.query.filter_by(feed = feed).all()
        for scoreFeed in scoreFeeds:
            scoreFeed.delete()

        # Now remove the feed from the database
        feed.delete()
        session.commit()
        print "deleted %s" % feed.title

    except:
        session.rollback()
        print "error deleting feed!"

def _removeItem(item):
    """
    Function _removeItem, removes an article from the database.
    """
    try:
        # First remove all the scoreItems from the ScoreItem table.
        scoreItems = ScoreItem.query.filter_by(item = item).all()
        for scoreItem in scoreItems:
                item.delete()

        #then delete the item
        item.delete()
#        session.commit() #slows down the delete process when we commit each delete.
    except:
        print "Error deleting %s" % item.title
#        session.rollback()


def updateAll():
    """
    function to update the content of all the feeds in the subscribed list.
    """
    try:
        for feed in Feed.query.all():
            print "fetching updates for %s..." % feed.title
            updateFeed(feed)
        session.commit()
    except:
        session.commit()
        print "Error updating feeds"
    else:
        print "all %d feeds are up to date" % len(Feed.query.all())


def updateFeed(feed):
    """
    function to update the content of a feed
    """

    feedData = feedparser.parse(feed.url, etag = feed.etag, modified = time.localtime(feed.lastModified))
    try:
        if feedData.status == 301:
            print "feed url modified. trying the new url..."
            feedData = feedparser.parse(feedData.url, etag = feed.etag, modified = time.localtime(feed.lastModified))

        if feedData.status == 304:
            print "No updates"

        else:
            print feedData.status

            lastModified = time.localtime(feed.lastModified)
            feed.lastModified = time.mktime(feedData.modified)

            for item in feedData.entries:
                if item.updated_parsed > lastModified:
                    _addItem(feed, item)
                    print "Added %s to the database." % item.title #comment this later
    except AttributeError:
        print " Error fetching feeds, Network error???"

    #if feedData.status == 200:
    #    print "Site content has not been updated."
    #    pass


def listFeeds():
    """
    Function to return the List of subscribed feeds from the database.
    """
#    # hack to commit less. find a better way if possible
#    try:
#        session.commit()
#    except:
#        sesrion.rollback()

    feedList = Feed.query.all()
    return feedList


def listItems(i=-1):
    """
    Function to return the List of fetched articles on the database.
    Optional argument will define from wich feed the articles should be returned.
    """
#    # hack to commit less. find a better way if possible
#    try:
#        session.commit()
#    except:
#        session.rollback()

    itemList = []
    if i is (-1):
        itemList = Item.query.order_by(Item.updated).all()
        itemList.reverse()
    else:
        q = Item.query.filter_by(feed = i)
        itemList = q.order_by(Item.updated).all()
        itemList.reverse()
    return itemList


def listNew(i=-1):
    """
    Function to return the List of fetched articles on the database.
    Optional argument will define from wich feed the articles should be returned.
    """
#    # hack to commit less. find a better way if possible
#    try:
#        session.commit()
#    except:
#        sesrion.rollback()

    itemList = []
    if i is (-1):
        itemList = Item.query.filter_by(age = 0).order_by(Item.updated).all()
        itemList.reverse()
    else:
        q = Item.query.filter_by(feed = i, age = 0)
        itemList = q.order_by(Item.updated).all()
        itemList.reverse()
    return itemList


def listUnread(i=-1):
    """
    Function to return the List of fetched articles on the database.
    Optional argument will define from wich feed the articles should be returned.
    """
#    # hack to commit less. find a better way if possible
#    try:
#        session.commit()
#    except:
#        sesrion.rollback()

    itemList = []
    if i is (-1):
        itemList = Item.query.filter_by(age = 1).order_by(Item.updated).all()
        itemList.reverse()
    else:
        q = Item.query.filter_by(feed = i, age = 1)
        itemList = q.order_by(Item.updated).all()
        itemList.reverse()
    return itemList



def listRead(i=-1):
    """
    Function to return the List of already read articles.
    Optional argument will define from wich feed the articles should be returned.
    """
#    # hack to commit less. find a better way if possible
#    try:
#        session.commit()
#    except:
#        sesrion.rollback()

    itemList = []
    if i is (-1):
        itemList = Item.query.filter_by(age = 2).order_by(Item.updated).all()
        itemList.reverse()
    else:
        q = Item.query.filter_by(feed = i, age = 2)
        itemList = q.order_by(Item.updated).all()
        itemList.reverse()
    return itemList


def setItemFlag(item, age = 2, commit = True):
    """
    Function to set an article as new unred or old. set the flag as 0, 1, or 2
    as follows,

    new         0
    unread      1
    read        2

    """

    item.age = age
    if age is 2:
        item.isUnread = False
    elif age is (0 or 1):
        item.isUnread = True

    if commit is True:
        try:
            session.commit() # disabled individual commits to increse performance.
        except:
            session.rollback()
            print "Error in setItemFlags"


def main():
    initDB()

if __name__ == "__main__":
    main()

