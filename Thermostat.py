__author__ = 'Adam'

import time
import datetime
import json
import urllib2
from threading import Thread
from Temperature import Temperature


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
        self._notify_callback = None
        self._read_errors = 0

    def _monitor(self):
        while self._monitor_active:
            print("Starting thermostat write")
            self._write_thermostat()
            time.sleep(self._monitor_period * 1 / 10)
            print("Starting thermostat read")
            if self._read_thermostat():
                self._read_errors = 0
            else:
                self._read_errors += 1

            if self._read_errors == 5:
                self.notify("Haven't made contact with thermostat in 5 cycles")

            time.sleep(self._monitor_period * 9 / 10)

    def _read_thermostat(self):
        read_successful = False
        try:
            response = urllib2.urlopen('http://' + self._ip_address + '/tstat')
        except:
            return read_successful
        line = response.readline()
        print(line)
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
            #Compare to current date and time
            t1 = datetime.datetime.now()
            d = datetime.datetime.weekday(t1)
            h = t1.hour
            m = t1.minute

            if abs(int(self.current_time['minute']) - m) > 5 or int(self.current_time['hour']) != h or int(self.current_time['day']) != d:
                self.set_time(d, h, m)
                self._write_thermostat()
                self.notify("Thermostat time; day:%d hour:%d minute:%d" % (self.current_time['day'], self.current_time['hour'], self.current_time['minute']))
                self.notify("Correcting time; day:%d hour:%d minute:%d" % (d, h, m))

        #print self.current_temp.fahrenheit
        print ("Current temp in celsius: " + str(self.current_temp.celsius))
        return read_successful

    def _write_thermostat(self):
        if self.command == '':
            print ("Nothing to write")
            return None

        print ("Writing command")
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
        print("New command: " + self.command)

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