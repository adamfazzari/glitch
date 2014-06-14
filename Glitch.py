__author__ = 'Adam'

from Thermostat import Thermostat
from Weather import WeatherMonitor
from Thingspeak import Thingspeak
from threading import Thread
from Pushover import Pushover
from ArduinoClient import ArduinoClient
from Proximity import Proximity
import time
import ConfigParser
import os
from flask import Flask, url_for
from flask import render_template

app = Flask(__name__)


class Glitch(object):

    def __init__(self):
        self.armed = False
        self.status = ''
        self._load_settings()

        #Pushover
        self.pushover = Pushover(self._pushover_token, self._pushover_client)

        #Thingspeak
        self.ts = Thingspeak(self._thingspeak_api_key)

        #Arduino
        self.arduino = ArduinoClient(self._arduino_ip_address, self._arduino_port)
        self.arduino.set_motion_detect_callback(self.motion_detected)

        #Proximity
        self.proximity = Proximity()
        self.proximity.set_motion_sensor(self.arduino, ('Living Room', 'Basement Hallway', 'Basement'))
        for s in self._ping_nodes:
            self.proximity.add_ping_node(s)

        #Thermostat
        self.tstat = Thermostat(self._thermostat_ip_address, self._thermostat_period_s)
        self.tstat._notify_callback = self.notify

        #Weather monitor
        self.weather = WeatherMonitor(self._city_code, self._weather_period_s)

        self.tstat.start_monitor()
        self.weather.start_monitor()

        self.notify("Can you hear me?")

        self._main_thread = Thread(target=self.thingspeak_thread)
        self._main_thread.start()

    def notify(self, message):
        self.pushover.send_message(message, "Glitch")

    def _load_settings(self):
        config = ConfigParser.ConfigParser()
        conf_file = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), "glitch.conf"))
        config.read(conf_file)
        self._thingspeak_api_key = self.ConfigSectionMap(config, "ThingSpeak")['key']
        self._thingspeak_period_s = int(self.ConfigSectionMap(config, "ThingSpeak")['period_s'])
        self._arduino_ip_address = self.ConfigSectionMap(config, "Arduino")['ip_address']
        self._arduino_port = int(self.ConfigSectionMap(config, "Arduino")['port'])
        self._thermostat_ip_address = self.ConfigSectionMap(config, "Thermostat")['ip_address']
        self._thermostat_period_s = int(self.ConfigSectionMap(config, "Thermostat")['period_s'])
        self._city_code = self.ConfigSectionMap(config, "Weather")['city_code']
        self._weather_period_s = int(self.ConfigSectionMap(config, "Weather")['period_s'])
        self._pushover_token = self.ConfigSectionMap(config, "Pushover")['token']
        self._pushover_client = self.ConfigSectionMap(config, "Pushover")['client']
        s = self.ConfigSectionMap(config, "Proximity")['ping_nodes']
        self._ping_nodes = str.split(s,':')

    def thingspeak_thread(self):
        # Wait 60 seconds to let things warm up
        time.sleep(60)

        while True:
            d = dict()
            d['field1'] = self.tstat.current_temp.celsius
            d['field2'] = self.tstat.set_point_temp.celsius
            d['field3'] = self.tstat.furnace_state
            d['field4'] = self.weather.current_temp.celsius
            d['field5'] = self.arduino._living_room_state
            d['field6'] = self.arduino._basement_hallway_state
            d['field7'] = self.arduino._basement_state
            #d['field8'] = int(self.proximity.is_anyone_home())
            print(d)
            self.ts.write(d)
            #Update thingspeak every 5 minutes
            time.sleep(self._thingspeak_period_s)

    def ConfigSectionMap(self, config, section):
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

    def motion_detected(self, location):
        if self.armed:
            self.arduino.set_motion_detect_callback(None)
            self.status = "Motion detected in " + location
            self.notify(self.status)

if __name__ == '__main__':
    g = Glitch()

    @app.route('/')
    @app.route('/<arm>')
    def helloworld(arm='none'):
        if arm == 'true':
            g.armed = True
        elif arm == 'false':
            g.armed = False
            g.status = ''
        #a = {'current_temp':g.tstat.current_temp.celsius, 'armed':g.armed}
        return render_template('glitch.html', current_temp=g.tstat.current_temp.celsius, armed=g.armed, message=g.status)

    app.run()

