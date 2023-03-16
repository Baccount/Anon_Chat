import argparse
from os import getcwd, path


from stem.process import launch_tor_with_config

from bridges.downloadbridges import DownloadBridges
from client.client import Client
from logging_msg import log_msg
from scrips.scripts import saveBridges, print_bootstrap_lines, ascii_client, force_kill_tor

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add an argument to specify a boolean value
parser.add_argument(
    "-t",
    "--test",
    action="store_true",
    dest="test_enabled",
    help="Enable testing mode, disables bridges",
)

try:
    # Parse the arguments
    args = parser.parse_args()

    # Store the boolean flag in a variable False by default
    test_enabled = False
    test_enabled = args.test_enabled
except Exception as e:
    log_msg("argparse", "error", f"Error: {e}")


# path to the tor binary
tor_dir = getcwd() + "/tor/tor"
obsf4 = getcwd() + "/tor/obfs4proxy"
geo_ip_file = getcwd() + "/tor/geoip"
geo_ipv6_file = getcwd() + "/tor/geoip6"


class ClientServer:
    def __init__(self, test=False):
        self.test = test
        ascii_client()
        self.tor_cfg = {
            "SocksPort": "9050",
            "ControlPort": "9051",
            "CookieAuthentication": "1",
            "AvoidDiskWrites": "1",
            "Log": "notice stdout",
            "GeoIPFile": f"{geo_ip_file}",
            "GeoIPv6File": f"{geo_ipv6_file}",
        }
        self.choose_bridges()

    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("Client_Start", "start", f"starting {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=self.tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout=250,  # Increase timeout, bridges take a while to connect
                init_msg_handler=print_bootstrap_lines,
            )
        except Exception as e:
            # tor is already running
            log_msg("ClientServer", "start", "Tor is already running")
            log_msg("ClientServer", "start", f"Error: {e}")
        # Add some space
        print("\n" * 2)
        if not self.test:
            # start the client if not testing
            client = Client()
            client.start()

    def choose_bridges(self):
        if self.test is False and test_enabled is False:
            # we are not testing
            # ask if we want to use bridges or if they want to use their own
            choice = input(
                "1. Get Bridges online \n2. Use your own bridges\n3. Default Tor Connection\n:"
            )

            if choice == "1":
                self.use_bridges()
            elif choice == "2":
                self.use_own_bridges()
            else:
                # use default tor config
                pass
            # if the user enters something else use default tor config
            log_msg("StartServer", "SocksPort", f"{self.tor_cfg['SocksPort']}")
            log_msg("StartServer", "ControlPort", f"{self.tor_cfg['ControlPort']}")

    def use_own_bridges(self):
        print("Get bridges from https://bridges.torproject.org/bridges/?transport=obfs4")
        bridges = input("Enter your bridges: ")
        saveBridges(bridge_lst=bridges)
        self.use_bridges()

    def use_bridges(self):
        # If bridges.json does not exist, download bridges
        if not path.exists("bridges.json"):
            db = DownloadBridges(protocol="obfs4")
            db.startBridges()
            if not db.checkCaptcha():
                print("Captcha is incorrect")
                self.use_bridges()
            db.saveBridges()
            db.cleanup()
            obsf4Bridges = db.readBridges()
        else:
            log_msg(
                "StartServer",
                "use_bridges",
                "bridges.json exists, using bridges from file",
            )
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
        log_msg("StartServer", "use_bridges", f"{self.tor_cfg['Bridge']}")




if __name__ == "__main__":
    try:
        client = ClientServer()
        client.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        force_kill_tor()
        exit(1)
