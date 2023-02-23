from server.server import Server
import os
from stem.process import launch_tor_with_config
from logging_msg import log_msg

# path to the tor binary
tor_dir = os.getcwd() + '/tor/tor'
obsf4 = os.getcwd() + '/tor/obfs4proxy'
geo_ip_file = os.getcwd() + '/tor/geoip'
geo_ipv6_file = os.getcwd() + '/tor/geoip6'
# create a new Tor configuration
tor_cfg = {
    'SocksPort': '9050',
    'ControlPort': '9051',
    'CookieAuthentication': '1',
    'ClientTransportPlugin': f'obfs4 exec {obsf4}',
    'Bridge': 'obfs4 [2a0c:4d80:42:702::1]:27015 C5B7CD6946FF10C5B3E89691A7D3F2C122D2117C cert=TD7PbUO0/0k6xYHMPW3vJxICfkMZNdkRrb63Zhl5j9dW3iRGiCx0A7mPhe5T2EDzQ35+Zw iat-mode=0',
    'AvoidDiskWrites': '1',
    'Log': 'notice stdout',
    'GeoIPFile': f'{geo_ip_file}',
    'GeoIPv6File': f'{geo_ipv6_file}',
}
log_msg("StartServer", "SocksPort", f"{tor_cfg['SocksPort']}")
log_msg("StartServer", "ControlPort", f"{tor_cfg['ControlPort']}")
class StartServer():
    def __init__(self):
        pass

    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("Onion", "connect", f"starting tor bin {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout=60,
            )
        except Exception as e:
            print(e)
        try:
            server = Server()
            server.start()
        except KeyboardInterrupt:
            print("\nExiting...")
            self.kill_tor()
            log_msg("Tor", "killed tor subprocess")
            exit(0)

    def kill_tor(self):
        try:
            self.tor_bin.kill()
        except Exception as e:
            print(e)



if __name__ == '__main__':
    server = StartServer()
    server.start()