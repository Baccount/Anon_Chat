import argparse
from json import dump
from os import getcwd, path

from colorama import Fore, Style
from stem.process import launch_tor_with_config

from bridges.downloadbridges import DownloadBridges
from client.client import Client
from kill_tor import force_kill_tor
from logging_msg import log_msg

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
        self.show_ascii()
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
                init_msg_handler=self.print_bootstrap_lines,
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
        self.saveBridges(bridge_lst=bridges)
        self.use_bridges()

    def saveBridges(self, bridge_lst):
        """
        Save the bridges to a file
        """
        log_msg("StartServer", "saveBridges", "Saving bridges to bridges.json")
        # write the bridges from the file
        with open("bridges.json", "w") as f:
            dump(bridge_lst, f)

    def print_bootstrap_lines(self, line):
        if "Bootstrapped " in line:
            # print the line and clear it
            final_msg = f"{Fore.WHITE + Style.DIM}{line}{Style.RESET_ALL}"
            print(final_msg, end="\r")

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

    def show_ascii(self):
        print(
            """
               d8888                             .d8888b.  888               888    
              d88888                            d88P  Y88b 888               888    
             d88P888                            888    888 888               888    
            d88P 888 88888b.   .d88b.  88888b.  888        88888b.   8888b.  888888 
           d88P  888 888 "88b d88""88b 888 "88b 888        888 "88b     "88b 888    
          d88P   888 888  888 888  888 888  888 888    888 888  888 .d888888 888    
         d8888888888 888  888 Y88..88P 888  888 Y88b  d88P 888  888 888  888 Y88b.  
        d88P     888 888  888  "Y88P"  888  888  "Y8888P"  888  888 "Y888888  "Y888 \n"""
        )


if __name__ == "__main__":
    try:
        client = ClientServer()
        client.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        force_kill_tor()
        exit(1)
