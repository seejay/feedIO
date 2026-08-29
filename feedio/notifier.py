#!/usr/bin/python3
"""
notifier module for feedIO using PyQt6's QSystemTrayIcon for cross-platform support.
"""

__version__ = "2.0.0"

import logging
from PyQt6.QtWidgets import QSystemTrayIcon

class Notifier(object):
    def __init__(self, title="feedIO", description="", icon=None, tray_icon=None):
        self.title = title
        self.description = description
        self.icon = icon
        self.tray_icon = tray_icon

    def notify(self):
        """
        Show a notification using the provided QSystemTrayIcon.
        """
        if self.tray_icon:
            # icon can be QSystemTrayIcon.MessageIcon
            icon = QSystemTrayIcon.MessageIcon.Information
            self.tray_icon.showMessage(self.title, self.description, icon, 5000)
        else:
            logging.debug(f"Notification (no tray icon): {self.title} - {self.description}")

    def pushNotification(self):
        self.notify()

    def basicNotification(self):
        self.notify()

    def summeryNotification(self):
        self.notify()

    def iconNotification(self):
        self.notify()

    def feedNotification(self):
        self.notify()
