#!/usr/bin/python3
"""
Purification module for feedIO using BeautifulSoup.
"""

from bs4 import BeautifulSoup

SHORTEN_LENGTH = 100

def cleanText(text):
    """
    Clear tags and make text readable.
    """
    if not text:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    data = soup.get_text()
    data = data.strip()

    # remove common trailing links
    for suffix in ["More", "\tMore"]:
        if data.endswith(suffix):
            data = data[:-len(suffix)].strip()

    return data

def shorten(text, numChars=SHORTEN_LENGTH):
    """
    Shorten text to predefined size.
    """
    if not text:
        return ""
    return (text[:numChars] + '..') if len(text) > numChars else text
