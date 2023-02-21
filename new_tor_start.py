from stem.control import Controller
from stem import process
import os


def main():

    # path to the tor binary
    tor_dir = os.getcwd() + '/tor_bin/tor'
    # create a new Tor configuration
    tor_cfg = {
        'SocksPort': '9050',
        'ControlPort': '9051',
        'CookieAuthentication': '1',
    }

    # start Tor with the new configuration
    tor_process = process.launch_tor_with_config(
        config=tor_cfg,
        tor_cmd=tor_dir,  # path to your tor binary
        timeout=60
    )

    # connect to the Tor control port to confirm the configuration
    with Controller.from_port(port=9051) as tor_controller:
        tor_controller.authenticate()  # provide the password if necessary
        socks_port = tor_controller.get_conf('SocksPort')  # get the value of the SocksPort parameter
        print(f'Tor is listening on port {socks_port}')  # print the value of the SocksPort parameter
    tor_process.kill()  # kill the Tor process


    def main():
        pass

if __name__ == "__main__":
    main()