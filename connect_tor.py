# this is the where all the tor connect code goes
import socks
import socket

class Tor(object):

    def __init__(self):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_onion(self, onion):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
        socket.socket = socks.socksocket
        self.server = (onion, 80)
        self.socket.connect(self.server)