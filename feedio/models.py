#!/usr/bin/python3
"""
Database models for feedIO using SQLAlchemy 2.0.
"""

__version__ = "2.0.0"

import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Unicode, UnicodeText, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from sqlalchemy.ext.associationproxy import association_proxy

from . import config

Base = declarative_base()

class ScoreFeed(Base):
    __tablename__ = 'score_feed'
    score = Column(Integer, default=1)
    topic_title = Column(Unicode(100), ForeignKey('topic.title'), primary_key=True)
    feed_url = Column(Unicode(255), ForeignKey('feed.url'), primary_key=True)
    
    topic = relationship("Topic", back_populates="score_feeds")
    feed = relationship("Feed", back_populates="score_feeds")

    def __repr__(self):
        return f'<ScoreFeed "{self.topic_title} - {self.feed_url} - {self.score}">'

class ScoreItem(Base):
    __tablename__ = 'score_item'
    score = Column(Integer, default=1000)
    topic_title = Column(Unicode(100), ForeignKey('topic.title'), primary_key=True)
    item_url = Column(Unicode(255), ForeignKey('item.url'), primary_key=True)
    
    topic = relationship("Topic", back_populates="score_items")
    item = relationship("Item", back_populates="score_items")

    def __repr__(self):
        return f'<ScoreItem "{self.topic_title} - {self.item_url} - {self.score}">'

class Feed(Base):
    __tablename__ = 'feed'
    title = Column(Unicode(100))
    url = Column(Unicode(255), primary_key=True)
    description = Column(UnicodeText)
    etag = Column(Unicode(100))
    lastModified = Column(Float)
    numVotes = Column(Integer, default=1)
    frequency = Column(Integer, default=1)
    fetchInterval = Column(Integer, default=1)
    
    items = relationship("Item", back_populates="feed", cascade="all, delete-orphan")
    score_feeds = relationship("ScoreFeed", back_populates="feed", cascade="all, delete-orphan")
    
    topics = association_proxy('score_feeds', 'topic',
                             creator=lambda topic: ScoreFeed(topic=topic))

    def __repr__(self):
        return f'<Feed "{self.title}" - ({self.url})>'

class Item(Base):
    __tablename__ = 'item'
    title = Column(Unicode(100))
    url = Column(Unicode(255), primary_key=True)
    description = Column(UnicodeText)
    updated = Column(Float)
    author = Column(Unicode(100))
    generalScore = Column(Integer, default=1000)
    numVotes = Column(Integer, default=1)
    isUnread = Column(Boolean, default=True)
    bookMarked = Column(Boolean, default=False)
    age = Column(Integer, default=0)
    favourite = Column(Boolean, default=False)
    feed_url = Column(Unicode(255), ForeignKey('feed.url'))
    
    feed = relationship("Feed", back_populates="items")
    score_items = relationship("ScoreItem", back_populates="item", cascade="all, delete-orphan")
    
    topics = association_proxy('score_items', 'topic',
                            creator=lambda topic: ScoreItem(topic=topic))

    def __repr__(self):
        return f'<Item "{self.title}" - ({self.url})>'

class Topic(Base):
    __tablename__ = 'topic'
    title = Column(Unicode(100), primary_key=True)
    numVotes = Column(Integer, default=1)

    score_items = relationship("ScoreItem", back_populates="topic", cascade="all, delete-orphan")
    items = association_proxy('score_items', 'item',
                             creator=lambda item: ScoreItem(item=item))

    score_feeds = relationship("ScoreFeed", back_populates="topic", cascade="all, delete-orphan")
    feeds = association_proxy('score_feeds', 'feed',
                             creator=lambda feed: ScoreFeed(feed=feed))

    def __repr__(self):
        return f'<Topic "{self.title}">'

engine = create_engine(f"sqlite:///{config.DB_FILE}")
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

def initDB():
    config.ensure_dirs()
    Base.metadata.create_all(engine)
    logging.info("Database initialized.")

if __name__ == "__main__":
    initDB()
