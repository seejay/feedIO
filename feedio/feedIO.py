#!/usr/bin/python
"""
feedIO - A feed aggregator that tracks the user's reading tastes and prioritizes 
the content from future feed updates according to the recorded user preferences.
Written in Python and Qt.

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
import sys


USERDIR = os.path.join(os.path.expanduser("~"),".feedIO")
DBFILE = os.path.join(USERDIR,"feedIO.sqlite")


import ui
import models
import classifier


def main():
    """
    feedIO main method. Creates the user profile directory in ~/.feedIO ,
    initializes the database, and loads the main user interface.
    """
    if not os.path.isdir(USERDIR):
        os.mkdir(USERDIR)
    models.initDB()
    classifier.initTopics()
    ui.initUI()


if __name__ == "__main__":
    main()
