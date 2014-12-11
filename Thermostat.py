__author__ = 'Adam'

import time
import datetime
import json
import urllib2
import logging
from threading import Thread
from Temperature import Temperature

class Thermostat(object):

    def __init__(self, address, period_s):
        self.JSON_HEADER = {'Content-Type': 'application/json'}
        self.current_temp = Temperature()
        self.set_point_temp = Temperature()
        self.furnace_state = 0
        self.day = -1
        self.yesterday_runtime_min = 0
        self.command = ''
        self._monitor_thread = Thread(target=self._monitor)
        self._monitor_active = False
        self._ip_address = address
        self._monitor_period = period_s
        self._notify_callback = None
        self._read_errors = 0

    def _monitor(self):
        while self._monitor_active:
            logging.debug("Thermostat: Starting write")
            self._write_thermostat()
            time.sleep(self._monitor_period * 1 / 10)
            logging.debug("Thermostat: Starting read")
            if self._read_thermostat():
                self._read_errors = 0

                #Check for a date change
                if int(self.current_time['day']) <> self.day:
                    self.day = int(self.current_time['day'])
                    self._read_thermostat_runtime()

            else:
                self._read_errors += 1

            if self._read_errors == 5:
                logging.warning("Thermostat: Haven't made contact in 5 cycles")
                self.notify("Haven't made contact with thermostat in 5 cycles")

            time.sleep(self._monitor_period * 9 / 10)


    def _read_thermostat_runtime(self):
        try:
            response = urllib2.urlopen('http://' + self._ip_address + '/tstat/datalog')
        except:
            return False

        line = response.readline()
        logging.debug("Thermostat data log: " + line)
        jline = json.loads(line)
        jline = jline['yesterday'] if 'yesterday' in jline else jline
        jline = jline['heat_runtime'] if 'heat_runtime' in jline else jline
        logging.debug("Thermostat: jline: " + jline)
        minutes = int(jline['minutes']) if 'minutes' in jline else 0
        minutes += int(jline['hours']) * 60 if 'hours' in jline else 0
        self.yesterday_runtime_min = minutes
        logging.debug("Thermostat: Setting yesterday's runtime to " + str(minutes) + " minutes")
        return True

    def _read_thermostat(self):
        read_successful = False
        try:
            response = urllib2.urlopen('http://' + self._ip_address + '/tstat')
        except:
            return read_successful
        line = response.readline()
        logging.debug("Thermostat: " + line)
        jline = json.loads(line)
        if jline.has_key('temp'):
            if jline['temp'] != -1:
                self.current_temp.fahrenheit = float(jline['temp'])
                read_successful = True
        if jline.has_key('t_heat'):
            if jline['t_heat'] != -1:
                self.set_point_temp.fahrenheit = float(jline['t_heat'])
                read_successful = True
        if jline.has_key('tstate'):
            if jline['tstate'] != -1:
                self.furnace_state = int(jline['tstate'])
                read_successful = True

        self.current_time = jline['time']

        if self.current_time['day'] > -1 and self.current_time['hour'] > -1 and self.current_time['minute'] >-1:
            read_successful = True

        return read_successful

    def _write_thermostat(self):
        if self.command == '':
            logging.debug("Thermostat: Nothing to write")
            return None

        logging.debug("Thermostat: Writing command")
        #data = json.dumps(self.command)
        request = urllib2.Request('http://' + self._ip_address + '/tstat', self.command, self.JSON_HEADER)
        #Clear the command so we don't write it again
        self.command = ''
        return urllib2.urlopen(request)

    def start_monitor(self):
        self._monitor_active = True
        self._monitor_thread.start()

    def stop_monitor(self):
        self._monitor_active = False

    def set_time(self, day, hour, minute):
        d = {'day': day, 'hour': hour, 'minute': minute}
        self._add_command('time', d)

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
        d = dict()
        if self.command != '':
            d = json.loads(self.command)
        d[key] = value
        self.command = json.dumps(d)
        logging.debug("Thermostat: New command - " + self.command)

    def notify(self, message):
        if self._notify_callback:
            self._notify_callback(message)

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


    t = Thermostat('192.168.0.146', 60)
    #t.set_time(4,21,5)
    #t._write_thermostat()


    #print ("This is test number %d" % (2))