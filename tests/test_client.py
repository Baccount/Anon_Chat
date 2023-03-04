import sys
sys.path.append('../')

# trunk-ignore(flake8/E402)
from client.connect_tor import Tor



# run tests for client
def test_client_tor():
    # test tor connection
    tor = Tor()