from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from logging_msg import log_msg
from stem.control import Controller


class OnionServer:

    def __init__(self):
        self.port = self.get_available_port()
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate()

    def get_available_port(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            log_msg("CreateOnion", "get_available_port", f" Port: {s.getsockname()[1]}")
            return s.getsockname()[1]

    def start(self):
        onion = self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
        print("[Server] server is running......")
        print(f"Onion Service: {self.g(onion.service_id)}" + self.g(".onion"))
        


    def g(self, text):
    # return green text
        return "\033[92m" + text + "\033[0m"

    def get_port(self):
        return self.port

