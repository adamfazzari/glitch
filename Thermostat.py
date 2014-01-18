__author__ = 'Adam'

import time
import json
import urllib2


class Temperature():

    def f_get(self):
        return self.celsius * 9 / 5 + 32

    def f_set(self, value):
        self.celsius = (float(value)-32) * 5 / 9

    fahrenheit = property(f_get, f_set)

    def c_set(self, value):
        self.c_temp = float(value)

    def c_get(self):
        return self.c_temp

    celsius = property(c_get, c_set, doc="Celsius temperature")


class Thermostat(object):

    def __init__(self, address, period_s):
        self.current_temp = Temperature()
        self.set_point_temp = Temperature()
        self._monitor_active = False
        self._ip_address = address
        self._monitor_period = period_s
        pass

    def monitor_thread(self):
        while self._monitor_active:
            self.read_thermostat()
            time.sleep(self._monitor_period)

    def read_thermostat(self):
        response = urllib2.urlopen('http://' + self._ip_address  + '/tstat')
        line = response.readline()
        print(line)
        jline = json.loads(line)
        if jline['temp'] != -1:
            print jline['temp']
            self.current_temp.fahrenheit = float(jline['temp'])

        print self.current_temp.fahrenheit
        print self.current_temp.celsius

    def write_thermostat(self):
        pass

    def start_monitor(self):
        self._monitor_active = True