from onionshare_cli import Common
from onionshare_cli import Onion
from onionshare_cli import ModeSettings


# create a new onion service
common = Common()
new_onion = Onion(common)

mode = ModeSettings(common)
new_onion.connect()

print(new_onion.start_onion_service(mode="share", port=8080, mode_settings=mode, await_publication=True))