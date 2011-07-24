#!/usr/bin/python
"""
A piece of code to do the required manipulation tasks for feedIO.
currently provides,

    cleanText() function to clear any tags and make a text readable.

    shorten() function to short a long text into a predefined size.

To be used with the feedIO tts feature and for classification of the article text.
TODO: find better ways to do this.
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


import HTMLParser

SHORTEN_LENGTH = 100

class Purify(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def getData(self):
        return ''.join(self.fed)


# Function to clen an article text.        
def cleanText(text):
    """
    function to clear any tags and make a text readable.
    """
    p= Purify()
    p.feed(text)
    data = p.getData()
    data = data.strip()
    # remove the trailing "More" link appears in some feeds.
    stripped = data.strip("\tMore")
    
    #to fix the UnicodeEncodeError exception that occurs in some texts
    stripped = stripped.encode('utf8')
    
    return stripped

#function to summarize a text to be given a sneak peak.
def shorten(text, numChars=SHORTEN_LENGTH):
    """
    function to short a long text into a predefined size.
    """
    info = (text[:numChars] + '..') if len(text) > numChars else text
    return info
