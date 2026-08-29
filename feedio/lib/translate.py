#!/usr/bin/python3
"""
Translation module for feedIO.
Original Google Translate v1.0 API is defunct.
Stubbed out for now.
"""

class TranslationError(Exception):
    pass

class Translator(object):
    def __init__(self):
        pass

    def translate(self, message, lang_to='en', lang_from=''):
        """
        Stub for translation.
        """
        return message

class DetectionError(Exception):
    pass

class LanguageDetector(object):
    def __init__(self):
        pass

    def detect(self, message):
        """
        Stub for detection.
        """
        return None
