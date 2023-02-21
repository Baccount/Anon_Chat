import socket
from random import randint
from stem.control import Controller
from stem import process
import os, signal
from time import sleep
import subprocess

class CreateOnion():
    
    def __init__(self):
        # stop tor
        self.stop_tor()
        # start tor
        self.start_tor()
        sleep(2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = randint(10000, 65535)
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate()
        self.socket.bind(("127.0.0.1", self.port))
        self.socket.listen(10)
    def stop_tor(self):
        # iterating through each instance of the process
        try:
            name = "tor"
            for line in os.popen("ps ax | grep " + name + " | grep -v grep"):
                fields = line.split()
                # extracting Process ID from the output
                pid = fields[0]
                # terminating process
                os.kill(int(pid), signal.SIGKILL)
            print("Process Successfully terminated")
        except Exception as e:
            print(e)

    def start_tor(self):
        # path to the tor binary
        tor_dir = os.getcwd() + '/tor_bin/tor'
        # create a new Tor configuration
        tor_cfg = {
            'SocksPort': '9050',
            'ControlPort': '9051',
            'CookieAuthentication': '1',
        }

        # start Tor with the new configuration
        self.tor_procc = process.launch_tor_with_config(
            config=tor_cfg,
            tor_cmd=tor_dir,  # path to your tor binary
            timeout=60
        )

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