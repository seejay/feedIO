"""
SpeechEngine module for feedIO. Provides the interface to communicate with speech engine
using pyttsx3 for cross-platform support.
"""

__version__ = "2.0.0"

import logging
import pyttsx3
import threading

class SpeechEngine:
    def __init__(self, pitch=None, speed=200):
        self.engine = pyttsx3.init()
        # pyttsx3 doesn't have a direct 'pitch' setting in a cross-platform way 
        # that's consistent, but we can set rate.
        self.engine.setProperty('rate', speed)
        self._stop_event = threading.Event()

    def say(self, text):
        """
        Speak the provided text.
        """
        def _speak():
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"Speech engine error: {e}")

        # Running in a separate thread to avoid blocking the UI
        threading.Thread(target=_speak, daemon=True).start()

    def stop(self):
        """
        Stop the speech engine.
        """
        try:
            self.engine.stop()
        except Exception as e:
            logging.error(f"Error stopping speech engine: {e}")
