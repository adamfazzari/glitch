__author__ = 'Adam'

import socket
from threading import Thread


class ArduinoClient(object):

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening = False
        self.connect()

    def connect(self):
        self.socket.connect((self.ip_address, self.port))
        print ("Connected")
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
                msg = ''

if __name__ == "__main__":
    c = ArduinoClient()
    c.connect('192.168.0.214', 1213)