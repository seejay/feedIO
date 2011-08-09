#!/usr/bin/python
"""
Doctest unit tests for feedIO : classifier module
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



def test_classifier():
    """
    Classifying options such as add, remove on feeds,topics and items

    Method(s) tested:
        - classifier.addTopic()
        - classifier.listTopics()
        - classifier.removeTopic()
        - classifier.getTopic()
   
    >>> import sys
    >>> sys.path.append("../feedio")
    >>> import classifier as c
    >>> from models import *
    >>> initDB()
    
    ***It is ok to fail ONE test case as it raise due to print statements ***
    >>> c.addTopic("TestTopic")
    <type 'list'>
    
    >>> type(c.listTopics())
    <type 'list'>
    
    >>> c.removeTopic(Topic.query.filter_by(title = "TestTopic" ).first())
    removed Topic TestTopic
    
    >>> c.removeTopic("abracadabraarchievaled")
    Error removing Items
    
    >>> c.getTopic(Topic.query.first())
    >>> type(c.getTopic(Topic.query.first()))
    <type 'NoneType'>
    
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
