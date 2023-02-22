from onionshare.onion import Onion
from onionshare.common import Common
from onionshare.settings import Settings



def main():
    common = Common(verbose=True)
    onion = Onion(common)
    custom_settings = Settings(common)
    custom_settings.set("connection_type", "bundled")
    onion.connect(custom_settings=custom_settings)



if __name__ == "__main__":
    main()