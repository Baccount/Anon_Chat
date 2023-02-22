from server.server import Server
import os
from stem.process import launch_tor_with_config
import time
import colorama
from colorama import Fore, Back, Style

verbose = True
# path to the tor binary
tor_dir = os.getcwd() + '/tor/tor'
obsf4 = os.getcwd() + '/tor/obfs4proxy'
# create a new Tor configuration
tor_cfg = {
    'SocksPort': '9050',
    'ControlPort': '9051',
    'CookieAuthentication': '1',
    'ClientTransportPlugin': 'obfs4 exec {0}'.format(obsf4),
    'Bridge': 'obfs4 [2a0c:4d80:42:702::1]:27015 C5B7CD6946FF10C5B3E89691A7D3F2C122D2117C cert=TD7PbUO0/0k6xYHMPW3vJxICfkMZNdkRrb63Zhl5j9dW3iRGiCx0A7mPhe5T2EDzQ35+Zw iat-mode=0'
}
class StartServer():
    def __init__(self):
        pass

    def log(self, module, func, msg=None):
        """
        If verbose mode is on, log error messages to stdout
        """
        if verbose:
            timestamp = time.strftime("%b %d %Y %X")
            final_msg = f"{Fore.LIGHTBLACK_EX + Style.DIM}[{timestamp}]{Style.RESET_ALL} {Fore.WHITE + Style.DIM}{module}.{func}{Style.RESET_ALL}"
            if msg:
                final_msg = (
                    f"{final_msg}{Fore.WHITE + Style.DIM}: {msg}{Style.RESET_ALL}"
                )
            print(final_msg)
    def start(self):
        # start Tor with the new configuration if tor is not running
        self.log("Onion", "connect", f"starting {tor_dir} subprocess")
        try:
            tor_bin = launch_tor_with_config(
                config=tor_cfg,
                tor_cmd=tor_dir,  # path to your tor binary
                timeout=60
            )
        except Exception as e:
            print(e)
        try:
            server = Server()
            server.start()
        except KeyboardInterrupt:
            print("\nExiting...")
            tor_bin.kill()
            self.log("Tor", "killed tor subprocess")
            exit(0)



if __name__ == '__main__':
    server = StartServer()
    server.start()