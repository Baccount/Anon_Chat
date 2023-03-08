import socket
from stem.control import Controller
from logging_msg import log_msg
import subprocess
from stem import ProtocolError

import os


class BundledTorCanceled(Exception):
    """
    This exception is raised if onionshare is set to use the bundled Tor binary,
    and the user cancels connecting to Tor
    """


class CreateOnion():

    def __init__(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # get available port
            self.port = self.get_available_port()
            self.controller = Controller.from_port(port=9051)
            self.controller.authenticate()
            self.socket.bind(("127.0.0.1", self.port))
            self.socket.listen(10)
        except Exception as e:
            log_msg("CreateOnion", "__init__", f"Error: {e}")
            self.force_kill_tor()
            exit(1)

    def get_available_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            log_msg("CreateOnion", "get_available_port", f" Port: {s.getsockname()[1]}")
            return s.getsockname()[1]

    def force_kill_tor(self):
        """
        Force kill the tor process
        """
        try:
            log_msg("force_kill_tor", "Killing tor subprocess")
            # Find the process IDs (PIDs) of the processes with the given name
            pid_command = ["pgrep", "-x", "tor"]
            pid_process = subprocess.Popen(pid_command, stdout=subprocess.PIPE)
            pid_output, _ = pid_process.communicate()
            pids = pid_output.decode().strip().split("\n")
            # Kill each process with the found PIDs
            if pids:
                for pid in pids:
                    kill_command = ["kill", pid]
                    subprocess.run(kill_command)
                    print(f"Process tor (PID {pid}) killed.")
            else:
                print("No process named tor found.")

        except Exception as e:
            print(e)


    def ephemeral_onion(self):
        '''
        create ephemeral hidden services
        '''
        try:
            log_msg("ephemeral_onion", "Creating ephemeral hidden service on port 80")
            return self.controller.create_ephemeral_hidden_service({80: self.port}, await_publication = True)
        except ProtocolError as e:
            # kill tor subprocess
            log_msg("CreateOnion", "non_ephemeral_onion", f"Error: {e}")
            self.force_kill_tor()
            # call the function again
            self.ephemeral_onion()


    def non_ephemeral_onion(self):
        '''
        create non-ephemeral hidden services using a private key
        '''
        # set key path as the current directory
        try:
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
        except ProtocolError as e:
            # kill tor subprocess
            log_msg("CreateOnion", "non_ephemeral_onion", f"Error: {e}")
            self.force_kill_tor()
            # call the function again
            self.non_ephemeral_onion()
        return response