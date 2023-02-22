import requests
import sys
import os
import inspect
# connect tor using bridges
from stem.control import Controller
from stem import Signal
import time


# Common paths
root_path = os.path.dirname(
    os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
)
working_path = os.path.join(root_path, "build", "tor")

def update_tor_bridges():
    """
    Update the built-in Tor Bridges in OnionShare's torrc templates.
    """
    torrc_template_dir = root_path
    endpoint = "https://bridges.torproject.org/moat/circumvention/builtin"
    r = requests.post(
        endpoint,
        headers={"Content-Type": "application/vnd.api+json"},
    )
    if r.status_code != 200:
        print(
            f"There was a problem fetching the latest built-in bridges: status_code={r.status_code}"
        )
        sys.exit(1)

    result = r.json()
    print(f"Built-in bridges: {result}")

    if "errors" in result:
        print(
            f"There was a problem fetching the latest built-in bridges: errors={result['errors']}"
        )
        sys.exit(1)

    for bridge_type in ["meek-azure", "obfs4", "snowflake"]:
        if bridge_type in result and result[bridge_type]:
            if bridge_type == "meek-azure":
                torrc_template_extension = "meek_lite_azure"
            else:
                torrc_template_extension = bridge_type
            torrc_template = os.path.join(
                root_path,
                torrc_template_dir,
                f"torrc_template-{torrc_template_extension}",
            )

            with open(torrc_template, "w") as f:
                f.write(f"# Enable built-in {bridge_type} bridge\n")
                bridges = result[bridge_type]
                # Sorts the bridges numerically by IP, since they come back in
                # random order from the API each time, and create noisy git diff.
                bridges.sort(key=lambda s: s.split()[1])
                for item in bridges:
                    f.write(f"Bridge {item}\n")





def connect_tor():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())

        # set up the configuration for the obfs4 bridge
        conf = {
            'UseBridges': '1',
            'Bridge': 'obfs4 51.222.13.177:80 5EDAC3B810E12B01F6FD8050D2FD3E277B289A08',
            'ClientTransportPlugin': 'obfs4 exec /usr/bin/obfs4proxy'
        }

        # update the torrc configuration
        controller.set_conf('torrc', conf)
        controller.signal(Signal.RELOAD)
        time.sleep(controller.get_newnym_wait())

        # establish a new connection to Tor using the obfs4 bridge
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()

if __name__ == "__main__":
    update_tor_bridges()
    connect_tor()
