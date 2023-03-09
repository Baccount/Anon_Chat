import sys
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
        clientserver = ClientServer()
        clientserver.start(test=True)
        self.tor = ConnectTor(test=True)
        self.client = Client()


    def test_connect_onion(self):
        # test tor connection to duckduckgo
        self.tor.connect_onion("duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion")
        # kill tor
        self.tor.force_kill_tor()


    def test_decode(self):
        # test decode function
        buffer = '{"sender_id": "1", "sender_nickname": "test", "message": "test"} {"sender_id": "1", "sender_nickname": "test", "message": "test"}'
        assert self.client.decode(buffer) == ['{"sender_id": "1", "sender_nickname": "test", "message": "test"}', '{"sender_id": "1", "sender_nickname": "test", "message": "test"}']