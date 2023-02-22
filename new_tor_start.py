from onionshare_cli.onion import Onion
from onionshare_cli.common import Common



def main():
    common = Common(verbose=True)
    onion = Onion(common)

    onion.connect()



if __name__ == "__main__":
    main()