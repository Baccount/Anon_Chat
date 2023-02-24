from client.client import Client
import os
from stem.process import launch_tor_with_config
from logging_msg import log_msg


verbose = True
# path to the tor binary
tor_dir = os.getcwd() + '/tor/tor'
obsf4 = os.getcwd() + '/tor/obfs4proxy'
geo_ip_file = os.getcwd() + '/tor/geoip'
geo_ipv6_file = os.getcwd() + '/tor/geoip6'
# create a new Tor configuration
# 'Bridge': 'obfs4 [2a0c:4d80:42:702::1]:27015 C5B7CD6946FF10C5B3E89691A7D3F2C122D2117C cert=TD7PbUO0/0k6xYHMPW3vJxICfkMZNdkRrb63Zhl5j9dW3iRGiCx0A7mPhe5T2EDzQ35+Zw iat-mode=0',
# 'ClientTransportPlugin': f'obfs4 exec {obsf4}',
tor_cfg = {
    'SocksPort': '9050',
    'ControlPort': '9051',
    'CookieAuthentication': '1',
    'AvoidDiskWrites': '1',
    'Log': 'notice stdout',
    'GeoIPFile': f'{geo_ip_file}',
    'GeoIPv6File': f'{geo_ipv6_file}',
}
class ClientServer():
    def __init__(self):
        pass


    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("Client_Start", "start", f"starting {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout=60
            )
        except Exception as e:
            # tor is already running
            log_msg("ClientServer","start" ,f"Error: {e}")
        try:
            client = Client()
            client.start()
        except KeyboardInterrupt:
            log_msg("Client_Start", "start", "keyboard interrupt")
            print("\nExiting...")
            self.kill_tor()
            exit(1)

    def kill_tor(self):
        try:
            self.tor_bin.kill()
            log_msg("Client_Start","kill_tor", "killed tor subprocess")
        except Exception as e:
            print(e)



if __name__ == '__main__':
    client = ClientServer()
    client.start()