#!/usr/bin/python
"""
notifier module for feedIO. Used to notify the user of new feed updates and other
 events of the application.
"""

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
