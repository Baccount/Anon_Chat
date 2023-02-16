import socks
import socket
from random import randint
from stem.control import Controller

class ConnectTor():
    
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = randint(10000, 65535)
        self.controller = Controller.from_port(port = 9051)
        self.controller.authenticate()