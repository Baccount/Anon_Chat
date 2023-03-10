import sys
import subprocess
import time
sys.path.append('../')
# trunk-ignore(flake8/E402)
from client.connect_tor import ConnectTor
# trunk-ignore(flake8/E402)
from client_start import ClientServer
# trunk-ignore(flake8/E402)
from client.client import Client

class TestClient:
    def setup(self):
        # start tor
        clientserver = ClientServer(test=True)
        clientserver.start()
        self.client = Client()


    def test_connect_onion(self):
        # test tor connection to duckduckgo
        self.tor = ConnectTor(test=True)
        self.tor.connect_onion("duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion")
        # kill tor
        self.tor.force_kill_tor()


    def test_decode(self):
        # test decode function
        buffer = '{"sender_id": "1", "sender_nickname": "test", "message": "test"} {"sender_id": "1", "sender_nickname": "test", "message": "test"}'
        assert self.client.decode(buffer) == ['{"sender_id": "1", "sender_nickname": "test", "message": "test"}', '{"sender_id": "1", "sender_nickname": "test", "message": "test"}']

    def test_kill_tor(self):
        # start tor
        self.tor = ConnectTor(test=True)
        self.tor.force_kill_tor()
        time.sleep(1)
        # check if the tor process is running or not
        pid_command = ["pgrep", "-x", "tor"]
        pid_process = subprocess.Popen(pid_command, stdout=subprocess.PIPE)
        pid_output, _ = pid_process.communicate()
        pids = pid_output.decode().strip().split("\n")
        # If tor is killed then the pids list will be empty
        assert pids == ['']