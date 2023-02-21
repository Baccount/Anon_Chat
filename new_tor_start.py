from onionshare_cli import Common
from onionshare_cli import ModeSettings
from stem.control import Controller
import tempfile
import os
import psutil
import time
import subprocess
import traceback
import shlex

from packaging.version import Version

def main():
    # create a new onion object
    common = Common()
    # create a new mode settings object
    mode = ModeSettings(common)
    
    new_onion = Onion(common, mode)
    # connect to tor
    new_onion.connect()







class BundledTorBroken(Exception):
    """
    This exception is raised if onionshare is set to use the bundled Tor binary,
    but the process seems to fail to run.
    """

class Onion(object):
    """
    Onion is an abstraction layer for connecting to the Tor control port and
    creating onion services. OnionShare supports creating onion services by
    connecting to the Tor controller and using ADD_ONION, DEL_ONION.

    stealth: Should the onion service be stealth?

    settings: A Settings object. If it's not passed in, load from disk.

    bundled_connection_func: If the tor connection type is bundled, optionally
    call this function and pass in a status string while connecting to tor. This
    is necessary for status updates to reach the GUI.
    """

    def __init__(self, common, use_tmp_dir=False, get_tor_paths=None):
        self.common = common
        self.common.log("Onion", "__init__")

        self.use_tmp_dir = use_tmp_dir

        # Set the path of the tor binary, for bundled tor
        if not get_tor_paths:
            get_tor_paths = self.common.get_tor_paths
        (
            self.tor_path,
            self.tor_geo_ip_file_path,
            self.tor_geo_ipv6_file_path,
            self.obfs4proxy_file_path,
            self.snowflake_file_path,
            self.meek_client_file_path,
        ) = get_tor_paths()

        # The tor process
        self.tor_proc = None

        # The Tor controller
        self.c = None

        # Start out not connected to Tor
        self.connected_to_tor = False

        # Assigned later if we are using stealth mode
        self.auth_string = None

        # Keep track of onions where it's important to gracefully close to prevent truncated downloads
        self.graceful_close_onions = []
    def connect(
        self,
        custom_settings=None,
        config=None,
        connect_timeout=120,
        local_only=False,
    ):

            # Either use settings that are passed in, or use them from common
            if custom_settings:
                self.settings = custom_settings
            elif config:
                self.common.load_settings(config)
                self.settings = self.common.settings
            else:
                self.common.load_settings()
                self.settings = self.common.settings

            self.common.log(
                "Onion",
                "connect",
                f"connection_type={self.settings.get('connection_type')}",
            )

            # The Tor controller
            self.c = None

            # TODO remove this
            # set settings connection type to bundled
            self.settings.set("connection_type", "bundled")
            
            if self.settings.get("connection_type") == "bundled":
                # Create a torrc for this session
                if self.use_tmp_dir:
                    self.tor_data_directory = tempfile.TemporaryDirectory(
                        dir=self.common.build_tmp_dir()
                    )
                    self.tor_data_directory_name = self.tor_data_directory.name
                else:
                    self.tor_data_directory_name = self.common.build_tor_dir()
                self.common.log(
                    "Onion",
                    "connect",
                    f"tor_data_directory_name={self.tor_data_directory_name}",
                )

                # Create the torrc
                with open(self.common.get_resource_path("torrc_template")) as f:
                    torrc_template = f.read()
                self.tor_cookie_auth_file = os.path.join(
                    self.tor_data_directory_name, "cookie"
                )
                try:
                    self.tor_socks_port = self.common.get_available_port(1000, 65535)
                except Exception:
                    print("OnionShare port not available")
                    raise PortNotAvailable()
                self.tor_torrc = os.path.join(self.tor_data_directory_name, "torrc")

                # If there is an existing OnionShare tor process, kill it
                for proc in psutil.process_iter(["pid", "name", "username"]):
                    try:
                        cmdline = proc.cmdline()
                        if (
                            cmdline[0] == self.tor_path
                            and cmdline[1] == "-f"
                            and cmdline[2] == self.tor_torrc
                        ):
                            self.common.log(
                                "Onion", "connect", "found a stale tor process, killing it"
                            )
                            proc.terminate()
                            proc.wait()
                            break
                    except Exception:
                        pass

                if self.common.platform == "Windows" or self.common.platform == "Darwin":
                    # Windows doesn't support unix sockets, so it must use a network port.
                    # macOS can't use unix sockets either because socket filenames are limited to
                    # 100 chars, and the macOS sandbox forces us to put the socket file in a place
                    # with a really long path.
                    torrc_template += "ControlPort {{control_port}}\n"
                    try:
                        self.tor_control_port = self.common.get_available_port(1000, 65535)
                    except Exception:
                        print("OnionShare port not available")
                        raise PortNotAvailable()
                    self.tor_control_socket = None
                else:
                    # Linux and BSD can use unix sockets
                    torrc_template += "ControlSocket {{control_socket}}\n"
                    self.tor_control_port = None
                    self.tor_control_socket = os.path.join(
                        self.tor_data_directory_name, "control_socket"
                    )

                torrc_template = torrc_template.replace(
                    "{{data_directory}}", self.tor_data_directory_name
                )
                torrc_template = torrc_template.replace(
                    "{{control_port}}", str(self.tor_control_port)
                )
                torrc_template = torrc_template.replace(
                    "{{control_socket}}", str(self.tor_control_socket)
                )
                torrc_template = torrc_template.replace(
                    "{{cookie_auth_file}}", self.tor_cookie_auth_file
                )
                torrc_template = torrc_template.replace(
                    "{{geo_ip_file}}", self.tor_geo_ip_file_path
                )
                torrc_template = torrc_template.replace(
                    "{{geo_ipv6_file}}", self.tor_geo_ipv6_file_path
                )
                torrc_template = torrc_template.replace(
                    "{{socks_port}}", str(self.tor_socks_port)
                )
                torrc_template = torrc_template.replace(
                    "{{obfs4proxy_path}}", str(self.obfs4proxy_file_path)
                )
                torrc_template = torrc_template.replace(
                    "{{snowflake_path}}", str(self.snowflake_file_path)
                )

                with open(self.tor_torrc, "w") as f:
                    self.common.log("Onion", "connect", "Writing torrc template file")
                    f.write(torrc_template)

                    # Bridge support
                    if self.settings.get("bridges_enabled"):
                        f.write("\nUseBridges 1\n")
                        if self.settings.get("bridges_type") == "built-in":
                            use_torrc_bridge_templates = False
                            builtin_bridge_type = self.settings.get("bridges_builtin_pt")
                            # Use built-inbridges stored in settings, if they are there already.
                            # They are probably newer than that of our hardcoded copies.
                            if self.settings.get("bridges_builtin"):
                                try:
                                    for line in self.settings.get("bridges_builtin")[
                                        builtin_bridge_type
                                    ]:
                                        if line.strip() != "":
                                            f.write(f"Bridge {line}\n")
                                    self.common.log(
                                        "Onion",
                                        "connect",
                                        "Wrote in the built-in bridges from OnionShare settings",
                                    )
                                except KeyError:
                                    # Somehow we had built-in bridges in our settings, but
                                    # not for this bridge type. Fall back to using the hard-
                                    # coded templates.
                                    use_torrc_bridge_templates = True
                            else:
                                use_torrc_bridge_templates = True
                            if use_torrc_bridge_templates:
                                if builtin_bridge_type == "obfs4":
                                    with open(
                                        self.common.get_resource_path(
                                            "torrc_template-obfs4"
                                        )
                                    ) as o:
                                        f.write(o.read())
                                elif builtin_bridge_type == "meek-azure":
                                    with open(
                                        self.common.get_resource_path(
                                            "torrc_template-meek_lite_azure"
                                        )
                                    ) as o:
                                        f.write(o.read())
                                elif builtin_bridge_type == "snowflake":
                                    with open(
                                        self.common.get_resource_path(
                                            "torrc_template-snowflake"
                                        )
                                    ) as o:
                                        f.write(o.read())
                                self.common.log(
                                    "Onion",
                                    "connect",
                                    "Wrote in the built-in bridges from torrc templates",
                                )
                        elif self.settings.get("bridges_type") == "moat":
                            for line in self.settings.get("bridges_moat").split("\n"):
                                if line.strip() != "":
                                    f.write(f"Bridge {line}\n")

                        elif self.settings.get("bridges_type") == "custom":
                            for line in self.settings.get("bridges_custom").split("\n"):
                                if line.strip() != "":
                                    f.write(f"Bridge {line}\n")

                # Execute a tor subprocess
                self.common.log("Onion", "connect", f"starting {self.tor_path} subprocess")
                start_ts = time.time()
                if self.common.platform == "Windows":
                    # In Windows, hide console window when opening tor.exe subprocess
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    self.tor_proc = subprocess.Popen(
                        [self.tor_path, "-f", self.tor_torrc],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                    )
                else:
                    if self.common.is_snapcraft():
                        env = None
                    else:
                        env = {"LD_LIBRARY_PATH": os.path.dirname(self.tor_path)}

                    self.tor_proc = subprocess.Popen(
                        [self.tor_path, "-f", self.tor_torrc],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                    )

                # Wait for the tor controller to start
                self.common.log("Onion", "connect", f"tor pid: {self.tor_proc.pid}")
                time.sleep(2)

                return_code = self.tor_proc.poll()
                if return_code is not None:
                    self.common.log("Onion", "connect", f"tor process has terminated early: {return_code}")

                # Connect to the controller
                self.common.log("Onion", "connect", "authenticating to tor controller")
                try:
                    if (
                        self.common.platform == "Windows"
                        or self.common.platform == "Darwin"
                    ):
                        self.c = Controller.from_port(port=self.tor_control_port)
                        self.c.authenticate()
                    else:
                        self.c = Controller.from_socket_file(path=self.tor_control_socket)
                        self.c.authenticate()
                except Exception as e:
                    print("OnionShare could not connect to Tor:\n{}".format(e.args[0]))
                    print(traceback.format_exc())
                    raise BundledTorBroken(e.args[0])

                while True:
                    try:
                        res = self.c.get_info("status/bootstrap-phase")
                    except SocketClosed:
                        raise BundledTorCanceled()

                    res_parts = shlex.split(res)
                    progress = res_parts[2].split("=")[1]
                    summary = res_parts[4].split("=")[1]

                    # "\033[K" clears the rest of the line
                    print(
                        f"\rConnecting to the Tor network: {progress}% - {summary}\033[K",
                        end="",
                    )



                    if summary == "Done":
                        print("")
                        break
                    time.sleep(0.2)

                    # If using bridges, it might take a bit longer to connect to Tor
                    if self.settings.get("bridges_enabled"):
                        # Only override timeout if a custom timeout has not been passed in
                        if connect_timeout == 120:
                            connect_timeout = 150
                    if time.time() - start_ts > connect_timeout:
                        print("")
                        try:
                            self.tor_proc.terminate()
                            print(
                                "Taking too long to connect to Tor. Maybe you aren't connected to the Internet, or have an inaccurate system clock?"
                            )
                            raise BundledTorTimeout()
                        except FileNotFoundError:
                            pass

            elif self.settings.get("connection_type") == "automatic":
                # Automatically try to guess the right way to connect to Tor Browser
                automatic_error = "Could not connect to the Tor controller. Is Tor Browser (available from torproject.org) running in the background?"

                # Try connecting to control port
                found_tor = False

                # If the TOR_CONTROL_PORT environment variable is set, use that
                env_port = os.environ.get("TOR_CONTROL_PORT")
                if env_port:
                    try:
                        self.c = Controller.from_port(port=int(env_port))
                        found_tor = True
                    except Exception:
                        pass

                else:
                    # Otherwise, try default ports for Tor Browser, Tor Messenger, and system tor
                    try:
                        ports = [9151, 9153, 9051]
                        for port in ports:
                            self.c = Controller.from_port(port=port)
                            found_tor = True
                    except Exception:
                        pass

                    # If this still didn't work, try guessing the default socket file path
                    socket_file_path = ""
                    if not found_tor:
                        try:
                            if self.common.platform == "Darwin":
                                socket_file_path = os.path.expanduser(
                                    "~/Library/Application Support/TorBrowser-Data/Tor/control.socket"
                                )

                            self.c = Controller.from_socket_file(path=socket_file_path)
                            found_tor = True
                        except Exception:
                            pass

                # If connecting to default control ports failed, so let's try
                # guessing the socket file name next
                if not found_tor:
                    try:
                        if self.common.platform == "Linux" or self.common.platform == "BSD":
                            socket_file_path = (
                                f"/run/user/{os.geteuid()}/Tor/control.socket"
                            )
                        elif self.common.platform == "Darwin":
                            socket_file_path = (
                                f"/run/user/{os.geteuid()}/Tor/control.socket"
                            )
                        elif self.common.platform == "Windows":
                            # Windows doesn't support unix sockets
                            print(automatic_error)
                            raise TorErrorAutomatic()

                        self.c = Controller.from_socket_file(path=socket_file_path)

                    except Exception:
                        print(automatic_error)
                        raise TorErrorAutomatic()

                # Try authenticating
                try:
                    self.c.authenticate()
                except Exception:
                    print(automatic_error)
                    raise TorErrorAutomatic()

            else:
                # Use specific settings to connect to tor
                invalid_settings_error = "Can't connect to Tor controller because your settings don't make sense."

                # Try connecting
                try:
                    if self.settings.get("connection_type") == "control_port":
                        self.c = Controller.from_port(
                            address=self.settings.get("control_port_address"),
                            port=self.settings.get("control_port_port"),
                        )
                    elif self.settings.get("connection_type") == "socket_file":
                        self.c = Controller.from_socket_file(
                            path=self.settings.get("socket_file_path")
                        )
                    else:
                        print(invalid_settings_error)
                        raise TorErrorInvalidSetting()

                except Exception:
                    if self.settings.get("connection_type") == "control_port":
                        print(
                            "Can't connect to the Tor controller at {}:{}.".format(
                                self.settings.get("control_port_address"),
                                self.settings.get("control_port_port"),
                            )
                        )
                        raise TorErrorSocketPort(
                            self.settings.get("control_port_address"),
                            self.settings.get("control_port_port"),
                        )
                    print(
                        "Can't connect to the Tor controller using socket file {}.".format(
                            self.settings.get("socket_file_path")
                        )
                    )
                    raise TorErrorSocketFile(self.settings.get("socket_file_path"))

                # Try authenticating
                try:
                    if self.settings.get("auth_type") == "no_auth":
                        self.c.authenticate()
                    elif self.settings.get("auth_type") == "password":
                        self.c.authenticate(self.settings.get("auth_password"))
                    else:
                        print(invalid_settings_error)
                        raise TorErrorInvalidSetting()

                except MissingPassword:
                    print(
                        "Connected to Tor controller, but it requires a password to authenticate."
                    )
                    raise TorErrorMissingPassword()
                except UnreadableCookieFile:
                    print(
                        "Connected to the Tor controller, but password may be wrong, or your user is not permitted to read the cookie file."
                    )
                    raise TorErrorUnreadableCookieFile()
                except AuthenticationFailure:
                    print(
                        "Connected to {}:{}, but can't authenticate. Maybe this isn't a Tor controller?".format(
                            self.settings.get("control_port_address"),
                            self.settings.get("control_port_port"),
                        )
                    )
                    raise TorErrorAuthError(
                        self.settings.get("control_port_address"),
                        self.settings.get("control_port_port"),
                    )

            # If we made it this far, we should be connected to Tor
            self.connected_to_tor = True

            # Get the tor version
            self.tor_version = self.c.get_version().version_str
            self.tor_version = Version(self.tor_version)
            self.common.log("Onion", "connect", f"Connected to tor {self.tor_version}")

            # Do the versions of stem and tor that I'm using support ephemeral onion services?
            list_ephemeral_hidden_services = getattr(
                self.c, "list_ephemeral_hidden_services", None
            )
            self.supports_ephemeral = (
                callable(list_ephemeral_hidden_services) and self.tor_version >= Version("0.2.7.1")
            )

            # Do the versions of stem and tor that I'm using support v3 stealth onion services?
            try:
                res = self.c.create_ephemeral_hidden_service(
                    {1: 1},
                    basic_auth=None,
                    await_publication=False,
                    key_type="NEW",
                    key_content="ED25519-V3",
                    client_auth_v3="E2GOT5LTUTP3OAMRCRXO4GSH6VKJEUOXZQUC336SRKAHTTT5OVSA",
                )
                tmp_service_id = res.service_id
                self.c.remove_ephemeral_hidden_service(tmp_service_id)
                self.supports_stealth = True
            except Exception:
                # ephemeral stealth onion services are not supported
                self.supports_stealth = False

            # Does this version of Tor support next-gen ('v3') onions?
            # Note, this is the version of Tor where this bug was fixed:
            # https://trac.torproject.org/projects/tor/ticket/28619
            self.supports_v3_onions = self.tor_version >= Version("0.3.5.7")

            # Now that we are connected to Tor, if we are using built-in bridges,
            # update them with the latest copy available from the Tor API
            if (
                self.settings.get("bridges_enabled")
                and self.settings.get("bridges_type") == "built-in"
            ):
                self.update_builtin_bridges()


if __name__ == "__main__":
    main()