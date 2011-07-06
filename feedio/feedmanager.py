#!/usr/bin/python
"""
feedManager for feedIO. provides functionality to add, remove and fetch updates
 from feeds.
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
import os
import time
from lib import feedparser
from models import *


USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
DBFILE=os.path.join(USERDIR,"feedIO.sqlite")


def addFeed(feedUrl):
    """
    Function to add a new feed to the database.
    """
    try:
        feedData = feedparser.parse(feedUrl)
    except:
        #this never occurs since parser does not raise any exceptions when invalid url is sent
        print "Invalid feed Url!"

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
            print "Subscribed to \t %s " % (feedData.feed.title)
            fetchFeeds(newFeed, feedData)


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
        print "deleted %s" % feed.title
        feed.delete()
        session.commit()
    except:
        session.rollback()
        print "error deleting feed!"

def _removeItem(item):
    """
    Function _removeItem, removes an article from the database.
    """
    try:
        item.delete()
#        session.commit() #slows down the delete process when we commit each delete.
    except:
        print "Error deleting %s" % item.title
        #session.rollback()


def updateAll():
    """
    function to update the content of all the feeds in the subscribed list.
    """
    try:
        for feed in Feed.query.all():
            print "fetching updates for %s..." % feed.title
            updateFeed(feed)
    except:
        "Error updating feeds"
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
    feedList = Feed.query.all()
    return feedList


def listItems(i=-1):
    """
    Function to return the List of fetched articles on the database.
    Optional argument will define from wich feed the articles should be returned.
    """
    itemList = []
    if i is (-1):
        itemList = Item.query.order_by(Item.updated).all()
        itemList.reverse()
    else:
        q = Item.query.filter_by(feed = i)
        itemList = q.order_by(Item.updated).all()
        itemList.reverse()
    return itemList

def markItemRead(item):
    try:
        item.isUnread = False
        session.commit()
    except:
        session.rollback()
        print "mark unread failed"



def main():
    initDB()

if __name__ == "__main__":
    main()

