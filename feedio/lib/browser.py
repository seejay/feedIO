#!/usr/bin/python3
"""
Browser module for feedIO using requests for modern Python 3 support.
"""

import random
import requests

BROWSERS = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
)

TIMEOUT = 10

class BrowserError(Exception):
    def __init__(self, url, error):
        self.url = url
        self.error = error
        super().__init__(f"Error fetching {url}: {error}")

class Browser:
    def __init__(self, user_agent=BROWSERS[0], debug=False):
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5'
        }
        self.debug = debug

    def get_page(self, url, data=None):
        try:
            if data:
                response = requests.post(url, data=data, headers=self.headers, timeout=TIMEOUT)
            else:
                response = requests.get(url, headers=self.headers, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise BrowserError(url, str(e))

    def set_random_user_agent(self):
        self.headers['User-Agent'] = random.choice(BROWSERS)
        return self.headers['User-Agent']
