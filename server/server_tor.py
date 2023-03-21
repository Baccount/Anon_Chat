from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from stem.control import Controller
from logging_msg import log_msg
from stem import ProtocolError
from scrips.scripts import force_kill_tor
from os import path


class BundledTorCanceled(Exception):
    """
    This exception is raised if onionshare is set to use the bundled Tor binary,
    and the user cancels connecting to Tor
    """


class CreateOnion():

    def __init__(self):
        try:
            # get available port
            self.port = self.get_available_port()
            self.controller = Controller.from_port(port=9051)
            self.controller.authenticate()
        except Exception as e:
            log_msg("CreateOnion", "__init__", f"Error: {e}")
            force_kill_tor()
            exit(1)

    def get_available_port(self):
        with socket(AF_INET, SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            log_msg("CreateOnion", "get_available_port", f" Port: {s.getsockname()[1]}")
            return s.getsockname()[1]

    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.bind(("127.0.0.1", self.port))
            self.socket.listen(10)
            log_msg("ephemeral_onion", "Creating ephemeral hidden service on port 80")
            return self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
        except ProtocolError as e:
            # kill tor subprocess
            log_msg("CreateOnion", "non_ephemeral_onion", f"Error: {e}")
            force_kill_tor()
            # call the function again
            self.ephemeral_onion()


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.bind(("127.0.0.1", self.port))
            self.socket.listen(10)
            key_path = path.join(path.dirname(__file__), 'private_key')
            log_msg("non_ephemeral_onion", "Creating non-ephemeral hidden service on port 80")
            if not path.exists(key_path):
                response = self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
                with open(key_path, 'w') as key_file:
                    key_file.write('%s:%s' % (response.private_key_type, response.private_key))
                return response
            else:
                with open(key_path) as key_file:
                    key_type, key_content = key_file.read().split(':', 1)
                    log_msg("non_ephemeral_onion", f"Using existing private key {key_content}")
                response = self.controller.create_ephemeral_hidden_service({80: self.port}, key_type=key_type, key_content=key_content, await_publication = True)
        except ProtocolError as e:
            # kill tor subprocess
            log_msg("CreateOnion", "non_ephemeral_onion", f"Error: {e}")
            force_kill_tor()
            # call the function again
            self.non_ephemeral_onion()
        return response

    def get_port(self):
        return self.port


    def run_server(self):
        # TODO: create a flask server and run it
        
        
        
        
        
        onion = self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
        print("[Server] server is running......")
        print(f"Onion Service: {self.g(onion.service_id)}" + self.g(".onion"))
        port = self.get_port()
        from flask import Flask
        app = Flask(__name__)
        @app.route('/')
        def hello_world():
            return 'Hello, World!'
        app.run(port=port, host="127.0.0.1")

    def g(self, text):
    # return green text
        return "\033[92m" + text + "\033[0m"