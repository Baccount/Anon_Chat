from os import getcwd, path
from stem.process import launch_tor_with_config
from kill_tor import force_kill_tor
from bridges.downloadbridges import DownloadBridges
from logging_msg import log_msg
from server.server import Server
from colorama import Fore, Style
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# Add an argument to specify a boolean value
parser.add_argument('-t', '--test', action='store_true', dest='test_enabled',
                    help='Enable testing mode, disables bridges')

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


class StartServer:
    def __init__(self, test=False):
        self.show_ascii()
        self.test = test
        self.tor_cfg = {
            "SocksPort": "9050",
            "ControlPort": "9051",
            "CookieAuthentication": "1",
            "AvoidDiskWrites": "1",
            "Log": "notice stdout",
            "GeoIPFile": f"{geo_ip_file}",
            "GeoIPv6File": f"{geo_ipv6_file}",
        }
        if self.test is False and test_enabled is False:
            # we are not testing
            choice = input("Use bridges? (y/n) ")
            if choice == "y" or choice == "Y":
                self.use_bridges()
            # TODO improve logic
            log_msg("StartServer", "SocksPort", f"{self.tor_cfg['SocksPort']}")
            log_msg("StartServer", "ControlPort", f"{self.tor_cfg['ControlPort']}")

    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("StartServer", "start", f"starting tor bin {tor_dir}")
        log_msg("StartServer", "config tor", f"{self.tor_cfg}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=self.tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout = 250, # Increase timeout, bridges take a while to connect
                init_msg_handler = self.print_bootstrap_lines,
            )
        except Exception as e:
            log_msg("StartServer", "start", "Tor is already running")
            log_msg("StartServer", "start", f"Error: {e}")
        # Add some space
        print("\n" * 2)
        # start the server if we are Not testing
        log_msg("StartServer ", f"Are we testing: {self.test}")
        if self.test is False:
            # test_enabled uses ephemeral by default
            server = Server(test_enabled)
            server.start()
        if self.test:
            # we are testing
            return True

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
            # use bridges
            "ClientTransportPlugin": f"obfs4 exec {obsf4}",
            "UseBridges": "1",
            "Bridge": obsf4Bridges,
        }
        log_msg("StartServer", "use_bridges", f"{self.tor_cfg['Bridge']}")

    def show_ascii(self):
        print(
            """
               d8888                             .d8888b.  888               888          .d8888b.                                             
              d88888                            d88P  Y88b 888               888         d88P  Y88b                                            
             d88P888                            888    888 888               888         Y88b.                                                 
            d88P 888 88888b.   .d88b.  88888b.  888        88888b.   8888b.  888888       "Y888b.    .d88b.  888d888 888  888  .d88b.  888d888 
           d88P  888 888 "88b d88""88b 888 "88b 888        888 "88b     "88b 888             "Y88b. d8P  Y8b 888P"   888  888 d8P  Y8b 888P"   
          d88P   888 888  888 888  888 888  888 888    888 888  888 .d888888 888               "888 88888888 888     Y88  88P 88888888 888     
         d8888888888 888  888 Y88..88P 888  888 Y88b  d88P 888  888 888  888 Y88b.       Y88b  d88P Y8b.     888      Y8bd8P  Y8b.     888     
        d88P     888 888  888  "Y88P"  888  888  "Y8888P"  888  888 "Y888888  "Y888       "Y8888P"   "Y8888  888       Y88P    "Y8888  888     
            """)


if __name__ == "__main__":
    try:
        server = StartServer()
        server.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        # run the force kill tor function without creating a new instance of StartServer
        force_kill_tor()
        exit(1)