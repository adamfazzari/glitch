__author__ = 'Adam'

import urllib
import urllib2
import json


class Pushover(object):

    def __init__(self, token, user):
        self.JSON_HEADER = {'Content-Type': 'application/json'}
        self.token = token
        self.user = user

    def send_message(self, message, title):
        data = {'token': self.token,
                'user': self.user,
                'message': message,
                'title': title
                }
        d = urllib.urlencode(data)
        req = urllib2.Request('https://api.pushover.net/1/messages.json')
        return urllib2.urlopen(req, d)