import os

from stem.process import launch_tor_with_config

from bridges.downloadbridges import DownloadBridges
from client.client import Client
from logging_msg import log_msg
from colorama import Fore, Style
from kill_tor import force_kill_tor


# path to the tor binary
tor_dir = os.getcwd() + "/tor/tor"
obsf4 = os.getcwd() + "/tor/obfs4proxy"
geo_ip_file = os.getcwd() + "/tor/geoip"
geo_ipv6_file = os.getcwd() + "/tor/geoip6"


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
        if self.test is False:
            choice = input("Use bridges? (y/n) ")
            if choice == "y" or choice == "Y":
                self.use_bridges()

    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("Client_Start", "start", f"starting {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=self.tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout = 120, # timeout in seconds
                init_msg_handler = self.print_bootstrap_lines,
            )
        except Exception as e:
            # tor is already running
            log_msg("ClientServer", "start", f"Error: {e}")
        # Add some space
        print("\n" * 2)
        if not self.test:
            # start the client if not testing
            client = Client()
            client.start()

    def print_bootstrap_lines(self, line):
        if "Bootstrapped " in line:
            # print the line and clear it
            final_msg = f"{Fore.WHITE + Style.DIM}{line}{Style.RESET_ALL}"
            print(final_msg, end="\r")

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
    def show_ascii(self):
        print("""
               d8888                             .d8888b.  888               888    
              d88888                            d88P  Y88b 888               888    
             d88P888                            888    888 888               888    
            d88P 888 88888b.   .d88b.  88888b.  888        88888b.   8888b.  888888 
           d88P  888 888 "88b d88""88b 888 "88b 888        888 "88b     "88b 888    
          d88P   888 888  888 888  888 888  888 888    888 888  888 .d888888 888    
         d8888888888 888  888 Y88..88P 888  888 Y88b  d88P 888  888 888  888 Y88b.  
        d88P     888 888  888  "Y88P"  888  888  "Y8888P"  888  888 "Y888888  "Y888 \n""")
                                                                            
                                                                            
                                                                            

if __name__ == "__main__":
    try:
        client = ClientServer()
        client.start()
    except KeyboardInterrupt:
        print("\nExiting...")
        # run the force kill tor function without creating a new instance of StartServer
        force_kill_tor()
        exit(1)