#!/usr/bin/python

"""
Read It Later (RIL) module for feedIO.
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


API_KEY = 'f9fT6t40g092alT6a7d908ch34p1Ux04'
SESSION = None


import lib.readitlater.api as ril
import sys


class FeedIOError(Exception): pass
class LogInError(FeedIOError): pass


class RilSession:
    """
        RilSession class to sync items from the Database with Read It Later
        servers.
    """
    def __init__ (self, user, pw):
        self.session = ril.API(API_KEY, user, pw)
        try:
            self.session.auth()
        except:
            print "login Error!"
            raise LogInError

    def submitItem(self, item):
        self.session.add(item.url,item.title)

    def getItems(state="unread"):
        self.session.get(state)

    def setItemTag(self, item, tags):
        pass
