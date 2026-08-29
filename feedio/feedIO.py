#!/usr/bin/python3
"""
feedIO - A feed aggregator that tracks the user's reading tastes and prioritizes 
the content from future feed updates according to the recorded user preferences.
Written in Python and Qt.
"""

__version__ = "2.0.0"

import os
import sys
import logging

# Ensure feedio is in the path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feedio import config
from feedio import ui
from feedio import models
from feedio import classifier

def main():
    """
    feedIO main method. Creates the user profile directory,
    initializes the database, and loads the main user interface.
    """
    logging.basicConfig(level=logging.DEBUG)
    config.ensure_dirs()
    models.initDB()
    classifier.initTopics()
    ui.initUI()

if __name__ == "__main__":
    main()
