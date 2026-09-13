"""Versioned SQLite persistence with stable identities and per-thread sessions."""
from pathlib import Path
from sqlalchemy import (create_engine, Column, Integer, Float, Boolean, Text,
                        ForeignKey, UniqueConstraint, event, text)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from sqlalchemy.ext.associationproxy import association_proxy
from . import config

Base = declarative_base()
SCHEMA_VERSION = 2


class Feed(Base):
    __tablename__ = 'feed'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, default='')
    etag = Column(Text, default='')
    modified = Column(Text, default='')
    lastModified = Column(Float)
    last_success = Column(Float)
    last_error = Column(Text, default='')
    numVotes = Column(Integer, default=1)
    frequency = Column(Integer, default=1)
    fetchInterval = Column(Integer, default=1)
    items = relationship('Item', back_populates='feed', cascade='all, delete-orphan')
    score_feeds = relationship('ScoreFeed', back_populates='feed', cascade='all, delete-orphan')
    topics = association_proxy('score_feeds', 'topic', creator=lambda t: ScoreFeed(topic=t))


class Item(Base):
    __tablename__ = 'item'
    __table_args__ = (UniqueConstraint('feed_id', 'entry_id'), {'sqlite_autoincrement': True})
    id = Column(Integer, primary_key=True)
    entry_id = Column(Text, nullable=False, default=lambda: __import__('uuid').uuid4().hex)
    url = Column(Text, default='')
    title = Column(Text, default='Untitled article')
    description = Column(Text, default='')
    updated = Column(Float, default=0)
    author = Column(Text, default='')
    generalScore = Column(Integer, default=1000)
    numVotes = Column(Integer, default=1)
    isUnread = Column(Boolean, default=True)
    bookMarked = Column(Boolean, default=False)
    age = Column(Integer, default=0)
    favourite = Column(Boolean, default=False)
    feed_id = Column(Integer, ForeignKey('feed.id', ondelete='CASCADE'), nullable=False)
    feed = relationship('Feed', back_populates='items')
    score_items = relationship('ScoreItem', back_populates='item', cascade='all, delete-orphan')
    topics = association_proxy('score_items', 'topic', creator=lambda t: ScoreItem(topic=t))


class Topic(Base):
    __tablename__ = 'topic'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, nullable=False)
    numVotes = Column(Integer, default=1)
    score_items = relationship('ScoreItem', back_populates='topic', cascade='all, delete-orphan')
    score_feeds = relationship('ScoreFeed', back_populates='topic', cascade='all, delete-orphan')
    items = association_proxy('score_items', 'item', creator=lambda i: ScoreItem(item=i))
    feeds = association_proxy('score_feeds', 'feed', creator=lambda f: ScoreFeed(feed=f))


class ScoreFeed(Base):
    __tablename__ = 'score_feed'
    topic_id = Column(Integer, ForeignKey('topic.id', ondelete='CASCADE'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feed.id', ondelete='CASCADE'), primary_key=True)
    score = Column(Integer, default=1)
    topic = relationship('Topic', back_populates='score_feeds')
    feed = relationship('Feed', back_populates='score_feeds')


class ScoreItem(Base):
    __tablename__ = 'score_item'
    topic_id = Column(Integer, ForeignKey('topic.id', ondelete='CASCADE'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id', ondelete='CASCADE'), primary_key=True)
    score = Column(Integer, default=1000)
    topic = relationship('Topic', back_populates='score_items')
    item = relationship('Item', back_populates='score_items')


class Vote(Base):
    __tablename__ = 'vote'
    __table_args__ = (UniqueConstraint('topic_id', 'item_key'), {'sqlite_autoincrement': True})
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topic.id', ondelete='CASCADE'), nullable=False)
    item_key = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    feed_url = Column(Text, nullable=False)
    value = Column(Integer, nullable=False)


class Setting(Base):
    __tablename__ = 'setting'
    key = Column(Text, primary_key=True)
    value = Column(Text, nullable=False)


engine = None
session = scoped_session(sessionmaker(expire_on_commit=False))
Session = session


def make_engine(path):
    result = create_engine('sqlite:///' + str(path), connect_args={'timeout': 10})
    @event.listens_for(result, 'connect')
    def configure(connection, record):
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA busy_timeout=10000')
    return result


def initDB(path=None):
    """Only call while no workers are active. Upgrade a known legacy schema safely."""
    global engine
    destination = Path(path or config.DB_FILE)
    destination.parent.mkdir(parents=True, exist_ok=True)
    session.remove()
    if engine is not None:
        engine.dispose()
    from .migration import prepare_database
    prepare_database(destination)
    engine = make_engine(destination)
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(text(f'PRAGMA user_version={SCHEMA_VERSION}'))
    config.ensure_dirs()


def close():
    session.remove()
    if engine is not None:
        engine.dispose()
