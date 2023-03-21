from socket import AF_INET, SOCK_STREAM

from socks import setdefaultproxy, PROXY_TYPE_SOCKS5, socksocket
from scrips.scripts import force_kill_tor
from logging_msg import log_msg


class ConnectTor(object):
    def __init__(self, test=False):
        self.test = test
        try:
            setdefaultproxy(PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
            # trunk-ignore(flake8/F811)
            socket = socksocket
            self.socket = socket(AF_INET, SOCK_STREAM)
        except Exception as e:
            log_msg("CreateOnion", "__init__", f"Error: {e}")
            force_kill_tor()
            exit(1)

    def connect_onion(self, onion):
        """
        Description: Connect to the onion address

        Return: True if connected to the onion address else False
        """
        try:
            # connect to the onion address with auth string
            self.server = (onion, 80)
            log_msg("connect_tor", "connect_onion", f"connecting to {onion}")
            self.server = (onion, 80)
            self.socket.connect(self.server)
            return True
        except Exception as e:
            log_msg("connect_tor", "connect_onion", f"Error: {e}")
            # reset the socket
            setdefaultproxy(PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
            # trunk-ignore(flake8/F811)
            socket = socksocket
            self.socket = socket(AF_INET, SOCK_STREAM)
            log_msg("connect_tor", "connect_onion", "Reseting socket")
            return False
        if self.test:
            # were testing
            return True
