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
        if j.has_key('Living Room'):
            d = dict()
            d['field5'] = j['Living Room']
            self.thingspeak_client.write(d)

if __name__ == "__main__":
    c = ArduinoClient('192.168.0.214', 1213)
    #c.parse_message('{"Living Room":"1"}')
