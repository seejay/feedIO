#!/usr/bin/python
"""
Doctest unit tests for feedIO : prioritizer module
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

__author__ = "Viraj Senarathna <virajsrc@gmail.com>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Viraj Senarathna"]


def test_prioritizer():
    """
    Prioritizing the articles by calculating scores and set scores

    Method(s) tested:
        - prioritizer.listScoreItems()
        - prioritizer.prioritize()
        - prioritizer.setScores()

    >>> import sys
    >>> sys.path.append("../feedio")
    >>> import prioritizer
    >>> from models import *
    >>> initDB()
    >>> t = Topic.query.first()
    >>> p = prioritizer.Prioritizer(t)
    >>> type(p.listScoreItems())
    <type 'list'>
    >>> type(p.prioritize(p.listScoreItems()))
    <type 'list'>
    >>> p.setScores(p.listScoreItems())
    Saved article scores
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
