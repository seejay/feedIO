#!/usr/bin/python
"""
Doctest unit tests for feedIO : purify module
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


def test_purify():
    """
    Removing unwanted tags from text,making the urls to managable length and make text to a fixed length

    Method(s) tested:
        - purify.cleanText()
        - purify.shorten()
        - purify.shortenUrl()

    ***There are some negative test cases put intentionally***

    >>> import sys
    >>> sys.path.append("../feedio")
    >>> import purify as p

    >>> p.cleanText("Is not an easy task.you can&#8217;t agree with the last sentence and your life is not horrible, I&#8217;d really like to know more  about you [...] ")
    'Is not an easy task.you cant agree with the last sentence and your life is not horrible, Id really like to know more about you [...]'

    >>> p.cleanText("Is not an easy task.you can&#8217;t agree with the last sentence")
    'Is not an easy task.you can&#8217;t agree with the last sentence'

    >>> p.shorten("Testing string limit to 20 charactors",20)
    'Testing string limit..'

    >>> p.shorten("Testing string limit to 20 charactors",20)
    'Testing string limit to'

    >>> p.shortenUrl("http://docs.python.org/library/doctest.html")
    'http://tinyurl.com/9q8sxp'

    >>> p.shortenUrl("http://docs.python.org/library/doctest.html")
    'http://docs.python.org/library/doctest.html'

    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
