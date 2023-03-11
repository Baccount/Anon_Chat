import socks
import socket
import subprocess
from logging_msg import log_msg
from kill_tor import force_kill_tor

class ConnectTor(object):

    def __init__(self, test=False):
        self.test = test
        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            log_msg("CreateOnion", "__init__", f"Error: {e}")
            force_kill_tor()
            exit(1)

    def connect_onion(self, onion):
        log_msg("connect_tor", "connect_onion", f"connecting to {onion}")
        self.server = (onion, 80)
        self.socket.connect(self.server)
        if self.test:
            # were testing
            return True