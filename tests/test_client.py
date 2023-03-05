import sys
sys.path.append('../')
# trunk-ignore(flake8/E402)
from client.connect_tor import Tor
# trunk-ignore(flake8/E402)
from client_start import ClientServer



# run tests for client
def test_connect_onion():
    # start tor
    client = ClientServer()
    client.start(test=True)

    tor = Tor()
    # # # test tor connection to duckduckgo
    tor.connect_onion("duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion")
    # kill tor
    tor.force_kill_tor()