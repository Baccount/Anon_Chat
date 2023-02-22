import socket
from random import randint
from stem.control import Controller
import os

from onionshare.onion import Onion
from onionshare.common import Common
from onionshare.settings import Settings



class CreateOnion():

    def __init__(self):
        # TODO NEW CODE BELOW
        self.common = Common(verbose=True)
        self.onion = Onion(self.common)
        self.custom_settings = Settings(self.common)
        self.custom_settings.set("connection_type", "bundled")
        self.onion.connect(custom_settings=self.custom_settings)

        self.socket_port = randint(10000, 65535)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = self.onion.get_control_port()
        self.controller = Controller.from_port(port=self.port)
        self.controller.authenticate()
        self.socket.bind(("127.0.0.1", self.socket_port))
        self.socket.listen(10)


    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        return self.controller.create_ephemeral_hidden_service({80: self.socket_port}, await_publication = True)


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')

        if not os.path.exists(key_path):
            response = self.controller.create_ephemeral_hidden_service({80: self.socket_port}, await_publication = True)
            with open(key_path, 'w') as key_file:
                key_file.write('%s:%s' % (response.private_key_type, response.private_key))
            return response
        else:
            with open(key_path) as key_file:
                key_type, key_content = key_file.read().split(':', 1)
            response = self.controller.create_ephemeral_hidden_service({80: self.socket_port}, key_type=key_type, key_content=key_content, await_publication = True)

        return response