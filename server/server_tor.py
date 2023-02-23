import socket
from random import randint
from stem.control import Controller
from logging_msg import log_msg

import os


class BundledTorCanceled(Exception):
    """
    This exception is raised if onionshare is set to use the bundled Tor binary,
    and the user cancels connecting to Tor
    """


class CreateOnion():

    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = randint(10000, 65535)
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate()
        self.socket.bind(("127.0.0.1", self.port))
        self.socket.listen(10)


    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        log_msg("ephemeral_onion", "Creating ephemeral hidden service on port 80")
        return self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')
        log_msg("non_ephemeral_onion", "Creating non-ephemeral hidden service on port 80")
        if not os.path.exists(key_path):
            response = self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
            with open(key_path, 'w') as key_file:
                key_file.write('%s:%s' % (response.private_key_type, response.private_key))
            return response
        else:
            with open(key_path) as key_file:
                key_type, key_content = key_file.read().split(':', 1)
                log_msg("non_ephemeral_onion", f"Using existing private key {key_content}")
            response = self.controller.create_ephemeral_hidden_service({80: self.port}, key_type=key_type, key_content=key_content, await_publication = True)

        return response