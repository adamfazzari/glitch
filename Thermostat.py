__author__ = 'Adam'

import time
import json
import urllib2
from threading import Thread

class Temperature(object):

    def __init__(self):
        self.c_temp = 0

    def f_get(self):
        return self.celsius * 9 / 5 + 32
    def f_set(self, value):
        self.celsius = (float(value)-32) * 5 / 9
    fahrenheit = property(f_get, f_set)

    def c_set(self, value):
        self.c_temp = float(value)
    def c_get(self):
        return self.c_temp
    celsius = property(c_get, c_set)


class Thermostat(object):

    def __init__(self, address, period_s):
        self.JSON_HEADER = {'Content-Type': 'application/json'}
        self.current_temp = Temperature()
        self.set_point_temp = Temperature()
        self.furnace_state = 0
        self.command = ''
        self._monitor_thread = Thread(target=self._monitor)
        self._monitor_active = False
        self._ip_address = address
        self._monitor_period = period_s

    def _monitor(self):
        while self._monitor_active:
            self._write_thermostat()
            time.sleep(self._monitor_period * 1 / 10)
            self._read_thermostat()
            time.sleep(self._monitor_period * 9 / 10)

    def _read_thermostat(self):
        response = urllib2.urlopen('http://' + self._ip_address  + '/tstat')
        line = response.readline()
        print(line)
        jline = json.loads(line)
        if jline['temp'] != -1:
            #print jline['temp']
            self.current_temp.fahrenheit = float(jline['temp'])
            self.set_point_temp.fahrenheit = float(jline['t_heat'])
            self.furnace_state.fahrenheit = float(jline['tstate'])

        #print self.current_temp.fahrenheit
        print ("Current temp in celsius: " + str(self.current_temp.celsius))

    def _write_thermostat(self):
        if self.command == '':
            print ("Nothing to write")
            return None

        print ("Writing command")
        data = json.dumps(self.command)
        request = urllib2.Request('http://192.168.0.146/tstat', data, self.JSON_HEADER)
        #Clear the command so we don't write it again
        self.command = ''
        return urllib2.urlopen(request)

    def start_monitor(self):
        self._monitor_active = True
        self._monitor_thread.start()

    def stop_monitor(self):
        self._monitor_active = False

    def set_temperature(self, value_c):
        t = Temperature
        t.celsius = value_c
        self._add_command('t_heat', str(t.fahrenheit))

    def hold(self, value):
        if value == True or value == 1:
            v = str(1)
        elif value == False or value == 0:
            v = str(0)
        else:
            return
        self._add_command('hold', v)

    def _add_command(self, key, value):
        d = json.loads(self.command)
        d[key] = value
        self.command = json.dumps(d)
        print("New command: " + self.command)


if __name__ == '__main__':
    """
    JSON_HEADER = {'Content-Type': 'application/json'}
    value = {"t_heat": 72}
    data = json.dumps(value)
    print (value)
    #data = urllib.urlencode(value)
    print(data)
    request = urllib2.Request('http://192.168.0.146/tstat', data, JSON_HEADER)
    #response = urllib2.urlopen(request)
    #print(response.readline())
    """