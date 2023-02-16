import socket
from random import randint
from stem.control import Controller
import os

class CreateOnion():
    
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = randint(10000, 65535)
        self.controller = Controller.from_port(port = 9051)
        self.controller.authenticate()
    # TODO : Add create onion service function


    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        return self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        key_path = os.path.join(os.path.dirname(__file__), 'private_key')

        if not os.path.exists(key_path):
            response = self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
            with open(key_path, 'w') as key_file:
                key_file.write('%s:%s' % (response.private_key_type, response.private_key))
            return response
        else:
            with open(key_path) as key_file:
                key_type, key_content = key_file.read().split(':', 1)
            response = self.controller.create_ephemeral_hidden_service({80: self.port}, key_type=key_type, key_content=key_content, await_publication = True)

        return response