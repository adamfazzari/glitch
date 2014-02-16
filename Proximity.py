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
        self.pinger = Thread(target=self._ping_thread)
        self.pinger.start()

    def add_ping_node(self, ip_address):
        self.ping_nodes.append(ip_address)

    def _ping_thread(self):
        self._ping_nodes()
        time.sleep(300)

    def _ping_nodes(self):
        for node in self.ping_nodes:
            response = os.system("ping -c 1 " + node)
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
            return False

        return True
