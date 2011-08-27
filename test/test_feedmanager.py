#!/usr/bin/python
"""
Doctest unit tests for feedIO : feedmanager module
"""

__version__ = "0.0.5"

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

__author__ = "Viraj Senarathna <virajsrc@gmail.com>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Viraj Senarathna"]


def test_feedmanager():
    """
    Managing feed options such as add, remove,set flags and listing on feeds

    Method(s) tested:
        - feedmanager.addFeed()
        - feedmanager.removeFeed()
        - feedmanager.listFeed()
        - feedmanager.listNew()
        - feedmanager.listRead()
        - feedmanager.setItemFlag()

    >>> import sys
    >>> sys.path.append("../feedio")
    >>> import feedmanager as fm
    >>> from models import *
    >>> initDB()
    
    >>> fm.addFeed("ww.ooooooo.com")
    Error! Invalid feed URL

    ***It is ok to fail ONE test case as it raise due to print statements ***
    >>> fm.addFeed('http://feedparser.org/docs/examples/atom10.xml')
    Added General to Sample Feed
    Added Sample Feed to all topics
    Subscribed to Sample Feed 

    >>> fm.removeFeed("hp://abcdefghijklmnopqrstuvwxyz0123456789")
    error deleting feed!

    >>> fm.removeFeed(Feed.query.filter_by(url = 'http://feedparser.org/docs/examples/atom10.xml' ).first())
    deleted First entry title
    deleted Sample Feed

    >>> session.rollback()
    >>> type(fm.listFeeds())
    <type 'list'>

    >>> type(fm.listNew(i=-1))
    <type 'list'>

    >>> type(fm.listUnread(i=-1))
    <type 'list'>

    >>> type(fm.listRead(i=-1))
    <type 'list'>

    >>> fm.setItemFlag(Item.query.first(), age = 2,commit = True)
    >>> 
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
