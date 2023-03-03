import os
import subprocess

from stem.process import launch_tor_with_config

from bridges.downloadbridges import DownloadBridges
from logging_msg import log_msg
from server.server import Server

# path to the tor binary
tor_dir = os.getcwd() + "/tor/tor"
obsf4 = os.getcwd() + "/tor/obfs4proxy"
geo_ip_file = os.getcwd() + "/tor/geoip"
geo_ipv6_file = os.getcwd() + "/tor/geoip6"


class StartServer:
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

        choice = input("Use bridges? (y/n) ")
        if choice == "y" or choice == "Y":
            self.use_bridges()
        log_msg("StartServer", "SocksPort", f"{self.tor_cfg['SocksPort']}")
        log_msg("StartServer", "ControlPort", f"{self.tor_cfg['ControlPort']}")

    def start(self):
        # start Tor with the new configuration if tor is not running
        log_msg("StartServer", "start", f"starting tor bin {tor_dir}")
        try:
            self.tor_bin = launch_tor_with_config(
                config=self.tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
            )
        except Exception as e:
            print(e)
        try:
            server = Server()
            server.start()
        except KeyboardInterrupt:
            print("\nExiting...")
            self.force_kill_tor()
            log_msg("Tor", "killed tor subprocess")
            exit(1)

    def force_kill_tor(self):
        """
        Force kill the tor process
        """
        try:
            log_msg("force_kill_tor", "Killing tor subprocess")
            # Find the process IDs (PIDs) of the processes with the given name
            pid_command = ["pgrep", "-x", "tor"]
            pid_process = subprocess.Popen(pid_command, stdout=subprocess.PIPE)
            pid_output, _ = pid_process.communicate()
            pids = pid_output.decode().strip().split("\n")
            # Kill each process with the found PIDs
            if pids:
                for pid in pids:
                    kill_command = ["kill", pid]
                    subprocess.run(kill_command)
                    print(f"Process tor (PID {pid}) killed.")
            else:
                print("No process named tor found.")
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
            # use bridges
            "ClientTransportPlugin": f"obfs4 exec {obsf4}",
            "UseBridges": "1",
            "Bridge": obsf4Bridges,
        }


if __name__ == "__main__":
    server = StartServer()
    server.start()
