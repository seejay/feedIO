#!/usr/bin/python3
"""
feedManager for feedIO. provides functionality to add, remove and fetch updates
 from feeds.
"""

__version__ = "2.0.0"

import logging
import time
import feedparser
from .models import session, Feed, Item, Topic, ScoreFeed, ScoreItem
from .lib import autorss

class FeedIOError(Exception): pass
class FeedError(FeedIOError): pass

def addFeed(feedUrl):
    """
    Function to add a new feed to the database.
    """
    try:
        feedUrl = autorss.getRSSLink(feedUrl)
        feedData = feedparser.parse(feedUrl)
    except Exception as e:
        logging.error(f"Invalid feed Url: {e}")
        raise FeedError

    if not hasattr(feedData, 'feed') or not hasattr(feedData.feed, 'title'):
        logging.error("Invalid feed data received")
        raise FeedError

    try:
        # Check if already exists
        existing = session.query(Feed).filter_by(url=str(feedUrl)).first()
        if existing:
            logging.debug(f"{feedData.feed.title} already subscribed")
            raise FeedError

        last_mod = time.mktime(feedData.modified) if hasattr(feedData, 'modified') else time.time()
        etag = str(feedData.etag) if hasattr(feedData, 'etag') else ""

        newFeed = Feed(url=str(feedUrl), title=feedData.feed.title,
                      lastModified=last_mod,
                      etag=etag)

        session.add(newFeed)
        session.commit()

        # Get the topics list and assign the feed to all the available topics.
        topicsList = session.query(Topic).all()
        for topic in topicsList:
            if topic not in newFeed.topics:
                newFeed.topics.append(topic)
        session.commit()
        
        logging.debug(f"Subscribed to {feedData.feed.title}")
        fetchFeeds(newFeed, feedData)
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding feed: {e}")
        raise FeedError

def fetchFeeds(feed, feedData):
    for item in feedData.entries:
        _addItem(feed, item)
    session.commit()

def _addItem(feed, item):
    """
    Function _addItem, adds a new article to the database.
    """
    try:
        # Check if exists
        existing = session.query(Item).filter_by(url=item.link).first()
        if existing:
            return

        updated = time.time()
        if hasattr(item, 'updated_parsed') and item.updated_parsed:
            updated = time.mktime(item.updated_parsed)
        elif hasattr(item, 'published_parsed') and item.published_parsed:
            updated = time.mktime(item.published_parsed)

        newItem = Item(title=item.title,
                      url=item.link,
                      description=item.summary if hasattr(item, 'summary') else "",
                      feed=feed,
                      updated=updated)

        session.add(newItem)
        # Topics will be assigned later or here
        topics = session.query(Topic).all()
        for t in topics:
            newItem.topics.append(t)
            
    except Exception as e:
        logging.error(f"Error adding item {item.title}: {e}")

def removeFeed(feed):
    """
    Function to remove a subscribed feed from the database.
    """
    try:
        session.delete(feed)
        session.commit()
        logging.debug(f"Deleted {feed.title}")
    except Exception as e:
        session.rollback()
        logging.error(f"Error deleting feed: {e}")

def updateAll():
    """
    function to update the content of all the feeds in the subscribed list.
    """
    feeds = session.query(Feed).all()
    for feed in feeds:
        logging.debug(f"fetching updates for {feed.title}...")
        updateFeed(feed)
    session.commit()

def updateFeed(feed):
    """
    function to update the content of a feed
    """
    try:
        feedData = feedparser.parse(feed.url, etag=feed.etag, 
                                   modified=time.localtime(feed.lastModified) if feed.lastModified else None)
        
        if hasattr(feedData, 'status'):
            if feedData.status == 304:
                logging.debug("No updates")
                return
            if feedData.status == 301:
                feed.url = feedData.href
                
        if hasattr(feedData, 'modified'):
            feed.lastModified = time.mktime(feedData.modified)
        if hasattr(feedData, 'etag'):
            feed.etag = feedData.etag

        lastModified = feed.lastModified
        for item in feedData.entries:
            item_updated = time.time()
            if hasattr(item, 'updated_parsed') and item.updated_parsed:
                item_updated = time.mktime(item.updated_parsed)
            
            if item_updated > (lastModified or 0):
                _addItem(feed, item)
    except Exception as e:
        logging.error(f"Error updating feed {feed.title}: {e}")

def listFeeds():
    return session.query(Feed).all()

def listItems(feed=None):
    query = session.query(Item)
    if feed:
        query = query.filter_by(feed=feed)
    return query.order_by(Item.updated.desc()).all()

def listNew(feed=None):
    query = session.query(Item).filter_by(age=0)
    if feed:
        query = query.filter_by(feed=feed)
    return query.order_by(Item.updated.desc()).all()

def listUnread(feed=None):
    query = session.query(Item).filter_by(age=1)
    if feed:
        query = query.filter_by(feed=feed)
    return query.order_by(Item.updated.desc()).all()

def listRead(feed=None):
    query = session.query(Item).filter_by(age=2)
    if feed:
        query = query.filter_by(feed=feed)
    return query.order_by(Item.updated.desc()).all()

def setItemFlag(item, age=2, commit=True):
    if age not in (0, 1, 2):
        raise ValueError('Invalid read state')
    item.age = age
    if age == 2:
        item.isUnread = False
    else:
        item.isUnread = True
    if commit:
        session.commit()
