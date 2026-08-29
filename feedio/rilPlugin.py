#!/usr/bin/python3
"""
Read It Later (RIL) module for feedIO.
"""

__version__ = "2.0.0"

import logging
import os
from .lib.readitlater import api as ril

API_KEY = os.environ.get('FEEDIO_RIL_API_KEY', '')
SESSION = None

class FeedIOError(Exception): pass
class LogInError(FeedIOError): pass

class RilSession:
    """
        RilSession class to sync items with Read It Later servers.
    """
    def __init__(self, user, pw):
        self.session = ril.API(API_KEY, user, pw)
        try:
            self.session.auth()
        except Exception as e:
            logging.error(f"Login error: {e}")
            raise LogInError

    def submitItem(self, item):
        try:
            self.session.add(item.url, item.title)
        except Exception as e:
            logging.error(f"Error submitting item to RIL: {e}")

    def getItems(self, state="unread"):
        try:
            return self.session.get(state)
        except Exception as e:
            logging.error(f"Error getting items from RIL: {e}")
            return None
