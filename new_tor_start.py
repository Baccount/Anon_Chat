from onionshare_cli import Common
from onionshare_cli import Onion
from onionshare_cli import ModeSettings


# create a new onion object
common = Common()
new_onion = Onion(common)
# create a new mode settings object
mode = ModeSettings(common)
# connect to tor
new_onion.connect()

print(new_onion.start_onion_service(mode="share", port=8080, mode_settings=mode, await_publication=True))