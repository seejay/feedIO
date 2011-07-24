#!/usr/bin/python
"""
notifier module for feedIO. Used to notify the user of new feed updates and other
 events of the application.
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

__author__ = "Chamika Viraj"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Chamika Viraj"]


import sys
import pynotify
import time

class Notifier:
	def __init__(self, title = "feedIO", description = "", icon = "notification-message-email"):
		self.title = title
		self.description = description
		self.icon = icon

	def pushNotification(self):
		if not pynotify.init("x-canonical-append"):
			print error

		n = pynotify.Notification(self.title, self.description,self.icon);
		n.set_hint_string ("x-canonical-append", "true");
		#n.set_hint_string ("icon-multi", "true");

		n.show ()
		time.sleep (1)

	def basicNotification(self):
		if not pynotify.init ("summary-body"):
 			print error

		n = pynotify.Notification(self.title,self.description)
 	        n.show ()

	def summeryNotification(self):
		if not pynotify.init ("summary-only"):
 			print error

		n = pynotify.Notification(self.description)
 	        n.show ()

	def iconNotification(self):
		if not pynotify.init ("icon-summary"):
 			print error

		n = pynotify.Notification(self.description,"","notification-audio-play")
 	        n.show ()
 	        
	def feedNotification(self):
		if not pynotify.init ("icon-summary-body"):
 			print error

		n = pynotify.Notification(self.title, self.description, self.icon)
 	        n.show ()
