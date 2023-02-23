# this is the where all the tor connect code goes
import socks
import socket
from logging_msg import log_msg

class Tor(object):

    def __init__(self):
        pass
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log_msg("__init__", f"Connected to Socket {self.socket}")

    def connect_onion(self, onion):
        log_msg("connect_tor", "connect_onion", f"connecting to {onion}")
        self.server = (onion, 80)
        self.socket.connect(self.server)