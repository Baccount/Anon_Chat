from client.client import Client
import os
from stem.process import launch_tor_with_config




# path to the tor binary
tor_dir = os.getcwd() + '/tor/tor'
# create a new Tor configuration
tor_cfg = {
    'SocksPort': '9050',
    'ControlPort': '9051',
    'CookieAuthentication': '1',
}

# start Tor with the new configuration if tor is not running

try:
    tor_process = launch_tor_with_config(
        config=tor_cfg,
        tor_cmd=tor_dir,  # path to your tor binary
        timeout=60
    )
except Exception as e:
    print(e)


client = Client()
client.start()
