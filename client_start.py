import os

from stem.process import launch_tor_with_config

from bridges.downloadbridges import DownloadBridges
from client.client import Client
from logging_msg import log_msg

verbose = True
# path to the tor binary
tor_dir = os.getcwd() + "/tor/tor"
obsf4 = os.getcwd() + "/tor/obfs4proxy"
geo_ip_file = os.getcwd() + "/tor/geoip"
geo_ipv6_file = os.getcwd() + "/tor/geoip6"


class ClientServer:
    def __init__(self):
        self.tor_cfg = {
            "SocksPort": "9050",
            "ControlPort": "9051",
            "CookieAuthentication": "1",
            "AvoidDiskWrites": "1",
            "Log": "notice stdout",
            "GeoIPFile": f"{geo_ip_file}",
            "GeoIPv6File": f"{geo_ipv6_file}",
        }

        # choice = input("Use bridges? (y/n) ")
        # if choice == "y" or choice == "Y":
        #     self.use_bridges()

    def start(self, test=False):
        # start Tor with the new configuration if tor is not running
        log_msg("Client_Start", "start", f"starting {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=self.tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout=60,
            )
        except Exception as e:
            # tor is already running
            log_msg("ClientServer", "start", f"Error: {e}")
        try:
            if not test:
                # start the client if not testing
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
            log_msg("Client_Start", "kill_tor", "killed tor subprocess")
        except Exception as e:
            print(e)

    def use_bridges(self):
        # If bridges.json does not exist, download bridges
        if not os.path.exists("bridges.json"):
            db = DownloadBridges(protocol="obfs4")
            db.startBridges()
            if not db.checkCaptcha():
                print("Captcha is incorrect")
                self.use_bridges()
            db.saveBridges()
            db.cleanup()
            obsf4Bridges = db.readBridges()
        else:
            log_msg("StartServer","use_bridges", "bridges.json exists, using bridges from file")
            db = DownloadBridges()
            obsf4Bridges = db.readBridges()
        self.tor_cfg = {
            "SocksPort": "9050",
            "ControlPort": "9051",
            "CookieAuthentication": "1",
            "AvoidDiskWrites": "1",
            "Log": "notice stdout",
            "GeoIPFile": f"{geo_ip_file}",
            "GeoIPv6File": f"{geo_ipv6_file}",
            "ClientTransportPlugin": f"obfs4 exec {obsf4}",
            "UseBridges": "1",
            "Bridge": obsf4Bridges,
        }


if __name__ == "__main__":
    client = ClientServer()
    client.start()
