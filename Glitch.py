__author__ = 'Adam'

from Thermostat import Thermostat
from Thingspeak import Thingspeak
from threading import Thread
import time
import ConfigParser
import os


class Glitch(object):

    def __init__(self):
        self._load_settings()

        self.ts = Thingspeak(self._thingspeak_api_key)
        self.tstat = Thermostat(self._thermostat_ip_address, 60)
        self.tstat.start_monitor()

        #Wait 1 minute to start the thingspeak thread, allow the thermostat time to read
        time.sleep(60)
        self._main_thread = Thread(target=self.thingspeak_thread)
        self._main_thread.start()

    def _load_settings(self):
        config = ConfigParser.ConfigParser()
        conf_file = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), "glitch.conf"))
        config.read(conf_file)
        self._thingspeak_api_key = self.ConfigSectionMap(config,"ThingSpeak")['key']
        self._thermostat_ip_address = self.ConfigSectionMap(config,"Thermostat")['ip_address']

    def thingspeak_thread(self):
        while True:
            d = dict()
            d['field1'] = self.tstat.current_temp.fahrenheit
            d['field2'] = self.tstat.set_point_temp.fahrenheit
            d['field3'] = self.tstat.furnace_state
            self.ts.write(d)
            #Update thingspeak every 5 minutes
            time.sleep(300)

    def ConfigSectionMap(self,config,section):
        dict1 = {}
        options = config.options(section)
        for option in options:
            try:
                dict1[option] = config.get(section, option)
                if dict1[option] == -1:
                    pass
                    #DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

if __name__ == '__main__':

    g = Glitch()

