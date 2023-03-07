import sys
sys.path.append('../')

# trunk-ignore(flake8/E402)
from server_start import StartServer



class TestServer():
# run tests for client
    def setup(self):
        self.server = StartServer(test=True)


    def test_server_tor(self):
        assert  self.server.start() is True



    def test_server_kill(self):
        assert self.server.force_kill_tor() is True
