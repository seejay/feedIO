#!/usr/bin/python

"""
database models for feedIO, uses python elixir. Currently has Entties for
 "Feed", "Item" and "Topic"

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


import os
from elixir import *
from sqlalchemy.ext.associationproxy import AssociationProxy

# path to the feedIO user profile
USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
DBFILE=os.path.join(USERDIR,"feedIO.sqlite")

class Feed(Entity):
    """
    The Feed entity to store the meta data of a web feed
    """
    title = Field(Unicode(100))
    url = Field(Unicode(255), required=True, primary_key=True)
    description = Field(UnicodeText)
    etag = Field(Unicode(100))
    lastModified = Field(Float)
    numVotes = Field(Integer, default =1)
    frequency = Field(Integer, default =1) # calculated by the duration between articles publish times
    fetchInterval = Field(Integer, default =1) # user defined interval to fetch.
    items = OneToMany('Item')

    score_feed = OneToMany('ScoreFeed')
    topics = AssociationProxy('score_feed', 'topic',
                             creator=lambda topic: ScoreFeed(topic=topic))
    
    def __repr__(self):
        return '<Feed "%s" - (%s)>' % (self.title, self.url)


class Item(Entity):
    """
    The Item entity to store a fetched article (a feed item)
    """

    title = Field(Unicode(100))
    url = Field(Unicode(255), primary_key=True)
    description = Field(UnicodeText)
    updated = Field(Float) # Stores the seconds since EPOCH
    author = Field(Unicode(100))
    generalScore = Field(Integer, default =1000)
    numVotes = Field(Integer, default =1)
    isUnread = Field(Boolean, default=True)
    bookMarked = Field(Boolean, default=False)
    age = Field(Integer, default = 0)
    favourite = Field(Boolean,default=False)
    feed = ManyToOne('Feed')

    score_item = OneToMany('ScoreItem')
    topics = AssociationProxy('score_item', 'topic',
                            creator=lambda topic: ScoreItem(topic=topic))

    def __repr__(self):
        return '<Item "%s" - (%s)>' % (self.title, self.url)


class Topic(Entity):
    title = Field(Unicode(100), required=True, primary_key=True)
    numVotes = Field(Integer, default =1)

    score_item = OneToMany('ScoreItem')
    items = AssociationProxy('score_item', 'item',
                             creator=lambda item: ScoreItem(item=item))

    score_feed = OneToMany('ScoreFeed')
    feeds = AssociationProxy('score_feed', 'feed',
                             creator=lambda feed: ScoreFeed(feed=feed))

    def __repr__(self):
        return '<Topic "%s">' % self.title


class ScoreItem(Entity):
    """
    The ScoreItem entity to store the particular scores for an article under each topic.
    """
    score = Field(Integer, default =1000)
    topic = ManyToOne('Topic', primary_key=True)
    item = ManyToOne('Item', primary_key=True)

    def __repr__(self):
        return '<ScoreItem "%s - %s - %d">' % (self.topic.title, self.item.title, self.score)


class ScoreFeed(Entity):
    """
    The ScoreFeed entity to store the particular scores for a feed under each topic.
    """
    score = Field(Integer, default =1)
    topic = ManyToOne('Topic', primary_key=True)
    feed = ManyToOne('Feed', primary_key=True)

    def __repr__(self):
        return '<ScoreFeed "%s - %s - %d">' % (self.topic.title, self.feed.title, self.score)



def initDB():
    # code to make sure that the user profile dirctory ~/.feedIO exists
    if not os.path.isdir(USERDIR):
        os.mkdir(USERDIR)

    # exilir code to set things up
    metadata.bind = "sqlite:///%s" % DBFILE
    setup_all()

    # And if the database doesn't exist: create it.
    if not os.path.exists(DBFILE):
        create_all()

def main():
    initDB()

if __name__ == "__main__":
    print __doc__
    main()
