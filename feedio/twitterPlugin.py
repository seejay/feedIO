#!/usr/bin/python3
"""
Twitter module for feedIO using modern tweepy.
"""

__version__ = "2.0.0"

import logging
import os
import tweepy

CONSUMER_KEY = os.environ.get('FEEDIO_TWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = os.environ.get('FEEDIO_TWITTER_CONSUMER_SECRET', '')
ACCESS_KEY = ''
ACCESS_SECRET = ''
VERIFIER = ''

class TwitterPlugin():
    def __init__(self):
        self.auth = None

    def authenticate(self):
        self.auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, callback='oob')
        try:
            auth_url = self.auth.get_authorization_url()
            return auth_url
        except Exception as e:
            logging.error(f"Twitter auth error: {e}")
            return None

    def verify(self):
        global ACCESS_KEY, ACCESS_SECRET
        try:
            access_token, access_token_secret = self.auth.get_access_token(VERIFIER)
            ACCESS_KEY = access_token
            ACCESS_SECRET = access_token_secret
            return (ACCESS_KEY, ACCESS_SECRET)
        except Exception as e:
            logging.error(f"Invalid verifier: {e}")
            raise

    def tweet(self, status):
        """
        Function to tweet an article.
        """
        global ACCESS_KEY, ACCESS_SECRET
        try:
            api = self.get_api()
            if api:
                api.update_status(status=status)
                logging.debug("Tweet posted successfully")
        except Exception as e:
            logging.error(f"Error tweeting: {e}")

    def get_api(self):
        global ACCESS_KEY, ACCESS_SECRET
        if ACCESS_KEY and ACCESS_SECRET:
            auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
            return tweepy.API(auth)
        return None
