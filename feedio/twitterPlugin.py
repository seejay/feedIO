#!/usr/bin/python

"""
twitter module for feedIO.
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


CONSUMER_KEY = 'XnvjuONm8m7RNiKHf2mBw'
CONSUMER_SECRET = 'HnCtS1qWwpq5NFrUB6x76ONFlZ9LdnLk8UjLxVrw'
ACCESS_KEY = ''
ACCESS_SECRET = ''
VERIFIER = ''

import sys
import tweepy


class TwitterPlugin():
    def __init__(self):
        self.auth = None


    def authenticate(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth_url = self.auth.get_authorization_url()
        return auth_url


    def verify(self):
        """

        """
        verifier = VERIFIER
        print verifier
        try:
            self.auth.get_access_token(verifier)
            ACCESS_KEY = self.auth.access_token.key
            ACCESS_SECRET = self.auth.access_token.secret

        except tweepy.TweepError:
            print "Invalid verifier"
            raise

        return (ACCESS_KEY, ACCESS_SECRET)

    def tweet(self, status):
        """
        Function to twitter an article.
        """
        print ACCESS_KEY
        print ACCESS_SECRET
        print "are the keys"

        try:
            self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = tweepy.API(self.auth)
            print "twitter.tweet() called"
            api.update_status(status)
        except AttributeError:
            print "Error in tweeting from plugin."
