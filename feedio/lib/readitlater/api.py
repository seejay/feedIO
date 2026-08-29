#!/usr/bin/python3
"""
Read It Later (Pocket) API wrapper for feedIO.
"""

import logging
import requests

API_ENDPOINT = 'https://readitlaterlist.com/v2/'

class ReadItLaterError(Exception): pass
class AuthError(ReadItLaterError): pass

class API(object):
    def __init__(self, api_key, username, password):
        self.api_key = api_key
        self.username = username
        self.password = password

    def _call(self, method, **params):
        params.update({
            'apikey': self.api_key,
            'username': self.username,
            'password': self.password,
        })
        try:
            response = requests.get(f"{API_ENDPOINT}{method}", params=params, timeout=10)
            if response.status_code == 401:
                raise AuthError('Username and/or password is incorrect')
            response.raise_for_status()
            return response.json() if response.text else True
        except requests.exceptions.RequestException as e:
            logging.error(f"RIL API error: {e}")
            raise ReadItLaterError(str(e))

    def auth(self):
        return self._call('auth')

    def add(self, url, title=None):
        return self._call('add', url=url, title=title)

    def get(self, state=None):
        params = {}
        if state:
            params['state'] = state
        return self._call('get', **params)
