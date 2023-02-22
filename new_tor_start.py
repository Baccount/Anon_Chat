from onionshare.onion import Onion
from onionshare.common import Common
from onionshare.settings import Settings

from stem.control import Controller



def main():
    common = Common(verbose=True)
    onion = Onion(common)
    custom_settings = Settings(common)
    custom_settings.set("connection_type", "bundled")
    onion.connect(custom_settings=custom_settings)
    
    
    
    # connect to the Tor control port to confirm the configuration
    port = onion.get_control_port()
    with Controller.from_port(port=port) as tor_controller:
        # set the cookie file to /Users/brandon/Library/Application Support/OnionShare/tor_data/cookie
        tor_controller.authenticate()  # provide the password if necessary
        socks_port = tor_controller.get_conf('SocksPort')  # get the value of the SocksPort parameter
        print(f'Tor is listening on port {socks_port}')  # print the value of the SocksPort parameter
        # create a new hidden service
        onion_address = tor_controller.create_ephemeral_hidden_service(ports={80: 8080}, await_publication=True)
        print(f'Onion address: {onion_address}')  # print the onion address
        input('Press enter to stop the hidden service')



if __name__ == "__main__":
    main()