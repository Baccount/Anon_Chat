import requests
import sys
import os
import inspect


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


def load_tor_bridges():
    """
    Load the built-in Tor Bridges from OnionShare's torrc templates.
    """
    bridges = []
    for bridge_type in ["meek-azure", "obfs4", "snowflake"]:
        if bridge_type == "meek-azure":
            torrc_template_extension = "meek_lite_azure"
        else:
            torrc_template_extension = bridge_type
        torrc_template = os.path.join(
            root_path,
            torrc_template_dir,
            f"torrc_template-{torrc_template_extension}",
        )

        with open(torrc_template, "r") as f:
            for line in f.readlines():
                if line.startswith("Bridge "):
                    bridges.append(line.strip().split(" ")[1])
    return bridges

# connect tor using bridges
def connect_tor():
    bridges = load_tor_bridges()
    print(bridges)
    # tor = stem.control.Controller.from_port(port=9051)
    # tor.authenticate()
    # tor.set_options({
    #     'SocksPort': '

if __name__ == "__main__":
    update_tor_bridges()
