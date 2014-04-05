__author__ = 'Adam'

import urllib
import httplib
import logging


class Thingspeak(object):

    def __init__(self, api_key):
        self._api_key = api_key
        self._headers = {'Content-type':'application/x-www-form-urlencoded','Accept':'text/plain'}
        self._url = 'api.thingspeak.com:80'

    def write(self, fields):
        #fields is a dictionary
        fields['key'] = self._api_key
        params = urllib.urlencode(fields)
        logging.debug("Thingspeak: Params - " + params)
        conn = httplib.HTTPConnection(self._url)
        conn.request('POST','/update/',params,self._headers)
        reponse = conn.getresponse()
        conn.close()




