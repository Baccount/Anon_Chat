from server.server import Server
import os
import subprocess
from stem.process import launch_tor_with_config
from logging_msg import log_msg

# path to the tor binary
tor_dir = os.getcwd() + '/tor/tor'
obsf4 = os.getcwd() + '/tor/obfs4proxy'
geo_ip_file = os.getcwd() + '/tor/geoip'
geo_ipv6_file = os.getcwd() + '/tor/geoip6'
# create a new Tor configuration
    # 'ClientTransportPlugin': f'obfs4 exec {obsf4}',
    # 'Bridge': 'obfs4 51.15.9.232:80 D0C9F8AA6E940FA536E7D694EFE67F9DEAF7E4E0 cert=Nw7pKQvtWh2VapurRDPtnf8Z3eIykwqnZXEpqD68Vxfee8C03K2Z3krZ79s74Ixxs7ZsJw iat-mode=0',
tor_cfg = {
    'SocksPort': '9050',
    'ControlPort': '9051',
    'CookieAuthentication': '1',
    'AvoidDiskWrites': '1',
    'Log': 'notice stdout',
    'GeoIPFile': f'{geo_ip_file}',
    'GeoIPv6File': f'{geo_ipv6_file}',
    # use bridges
    'ClientTransportPlugin': f'obfs4 exec {obsf4}',
    'UseBridges': '1',
    'Bridge': 'obfs4 51.15.9.232:80 D0C9F8AA6E940FA536E7D694EFE67F9DEAF7E4E0 cert=Nw7pKQvtWh2VapurRDPtnf8Z3eIykwqnZXEpqD68Vxfee8C03K2Z3krZ79s74Ixxs7ZsJw iat-mode=0',
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



if __name__ == '__main__':
    server = StartServer()
    server.start()