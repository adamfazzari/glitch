__author__ = 'Adam'

import socket
import json
from threading import Thread


class ArduinoClient(object):

    def __init__(self, ip_address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening = False
        self.thingspeak_client = None
        self.ip_address = ip_address
        self.port = port
        self._basement_state = 0
        self._basement_hallway_state = 0
        self._living_room_state = 0

        self.connect()


    def connect(self):
        self.socket.connect((self.ip_address, self.port))
        print ("Connected")
        self.socket.send('Thank you for connecting\n')
        self.start_listener_thread()

    def start_listener_thread(self):
        listener = Thread(target=self.listener_thread)
        self.listening = True
        listener.start()

    def listener_thread(self):
        msg = ''
        while self.listening:
            msg = msg + self.socket.recv(1024)
            if msg.endswith('\n'):
                print (msg)
                self.parse_message(msg)
                msg = ''

    def parse_message(self, message):
        j = json.loads(message)
        d = dict()
        if j.has_key('Living Room'):
            d['field5'] = j['Living Room']
            self._living_room_state = j['Living Room']
        if j.has_key('Basement Hallway'):
            d['field6'] = j['Basement Hallway']
            self._basement_hallway_state = j['Basement Hallway']
        if j.has_key('Basement'):
            d['field7'] = j['Basement']
            self._basement_state = j['Basement']
        if self.thingspeak_client:
            self.thingspeak_client.write(d)

if __name__ == "__main__":
    c = ArduinoClient('192.168.0.214', 1213)
    #c.parse_message('{"Living Room":"1"}')
