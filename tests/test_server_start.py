import sys

sys.path.append("../")

# trunk-ignore(flake8/E402)
from server_start import StartServer


class TestServer:
    # run tests for client
    def setup_method(self):
        self.server = StartServer(test=True)

    def test_server_tor(self):
        assert self.server.start() is True
