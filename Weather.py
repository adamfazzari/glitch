__author__ = 'Adam'

import urllib
from threading import Thread
from Temperature import Temperature
from xml.dom.minidom import parse
import time


class WeatherMonitor(object):

    def __init__(self, city_code, period_s):
        self.city_code = city_code
        self.period_s = period_s
        self.monitor_active = False
        self.current_temp = Temperature()
        self.monitor_thread = Thread(target=self._monitor)

    def _monitor(self):
        while self.monitor_active:
            self.current_temp.celsius = self._read_outside_temp(self.city_code)
            time.sleep(self.period_s)

    def start_monitor(self):
        self.monitor_active = True
        self.monitor_thread.start()

    def stop_monitor(self):
        self.monitor_active = False

    def _read_outside_temp(self, location_code):
        WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?p=%s'
        WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'
        METRIC = '&u=c'

        url = WEATHER_URL % location_code
        url = url + METRIC

        try:
                dom = parse(urllib.urlopen(url))
        except:
                return None

        ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]

        return ycondition.getAttribute('temp')

if __name__ == '__main__':
    ot = WeatherMonitor('CAXX0401', 30)
    print(ot._read_outside_temp('CAXX0401'))
