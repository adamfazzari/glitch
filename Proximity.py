__author__ = 'adam'

# This class takes care of figuring out if anyone is home based on various inputs

import datetime
import os
from threading import Thread
import time
import json

class Proximity(object):

    def __init__(self):
        self.motion_sensors = dict()
        self.last_ping_detected = datetime.datetime.now()
        self.last_motion_detected = datetime.datetime.now()
        self.last_motion_ended = datetime.datetime.now()
        self.ping_nodes = []
        self._state = 0 #0=no one home, 1=motion detected, 2=ping detected
        self._state_change_callback = None  #Callback when a new state has been detected, 0=People are home, 1=No one's home
        self.pinger = Thread(target=self._ping_thread)
        self.pinger.start()
        self.pinger_period = 300

    def add_ping_node(self, ip_address):
        self.ping_nodes.append(ip_address)

    def _ping_thread(self):
        while True:
            self._ping_nodes()
            state = self.is_anyone_home()
            if state == 2:
                #Ping less often if pink has been detected
                self.pinger_period = 300
            else:
                #Ping more often when no one's home or only motion has been detected
                self.pinger_period = 60

            if state != self._state and self._state_change_callback:
                self._state_change_callback(state)

            self._state = state

            time.sleep(self.pinger_period)

    def _ping_nodes(self):
        for node in self.ping_nodes:
            response = os.system("ping -c 1 -w 2 " + node + " > /dev/null 2>&1")
            if response == 0:
                self.last_ping_detected = datetime.datetime.now()

    def set_motion_sensor(self, motion_monitor, sensor_names):
        motion_monitor.message_received.addHandler(self.motion_event_handler)
        for s in sensor_names:
            self.motion_sensors[s] = 0

    def motion_event_handler(self, message):
        msg = json.loads(message)
        for k, v in msg.iteritems():
            if self.motion_sensors.has_key(k):
                self.motion_sensors[k] = v
                if v == 1:
                    print("Motion detected")
                    self.last_motion_detected = datetime.datetime.now()
                else:
                    # check to see if all motion has stopped
                    motion = 0
                    for k, v in self.motion_sensors.iteritems():
                        motion += int(v)
                    if motion == 0:
                        print("All motion ended")
                        self.last_motion_ended = datetime.datetime.now()

    def is_anyone_home(self):
        #Figures out based on various inputs if anyone is home
        #Returns 0 for no people detected, 1 for motion detected, 2 for ping detected
        motion = False
        if len(self.motion_sensors) > 0:
            motion = True
            td = datetime.datetime.now() - self.last_motion_ended
            if td.total_seconds() > 1800:
                motion = False

        ping = False
        if len(self.ping_nodes) > 0:
            ping = True
            td = datetime.datetime.now() - self.last_ping_detected
            if td.total_seconds() > 1800:
                ping = False

        if not ping and not motion:
            return 0

        if motion:
            return 1

        if ping:
            return 2
