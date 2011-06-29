#!/usr/bin/python

"""
Author  : Chanaka Jayamal
Date    : 20/05/2011

database models for teh feedIO reader, uses Elixir.
Currently has Entties for "Feed" and "Item" 

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


import os
from elixir import *

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
    items = OneToMany('Item')
    
    def __repr__(self):
        return '<Feed "%s" - (%s)>' % (self.title, self.url)

class Item(Entity):
    """
    The Item entity to store a fetched article (a feed item)
    """
    
    title = Field(Unicode(100))
    url = Field(Unicode(255),  primary_key=True)
    description = Field(UnicodeText)
    updated = Field(Float) # Stores the seconds since EPOCH
    generalScore = Field(Integer, default =1000)
    isUnread = Field(Boolean,default=True)
    feed = ManyToOne('Feed')
    topics = ManyToMany('Topic')
    
    def __repr__(self):
        return '<Item "%s" - (%s)>' % (self.title, self.url)

class Topic(Entity):
    """
    The Topic entity to store detils of a user interest topic
    """
    
    title = Field(Unicode(100))
    items = ManyToMany('Item')

    def __repr__(self):
        return '<Topic "%s">' % self.title


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
