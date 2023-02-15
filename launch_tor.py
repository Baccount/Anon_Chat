# Execute a tor subprocess
import time
import subprocess



tor_proc = subprocess.Popen(
    [tor_path, "-f", tor_torrc],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
)

# Wait for the tor controller to start
common.log("Onion", "connect", f"tor pid: {tor_proc.pid}")
time.sleep(2)

return_code = tor_proc.poll()
if return_code != None:
    common.log("Onion", "connect", f"tor process has terminated early: {return_code}")

# Connect to the controller
common.log("Onion", "connect", "authenticating to tor controller")
try:
    if (
        common.platform == "Windows"
        or common.platform == "Darwin"
    ):
        c = Controller.from_port(port=tor_control_port)
        c.authenticate()
    else:
        c = Controller.from_socket_file(path=tor_control_socket)
        c.authenticate()
except Exception as e:
    print("OnionShare could not connect to Tor:\n{}".format(e.args[0]))
    print(traceback.format_exc())
    raise BundledTorBroken(e.args[0])

while True:
    try:
        res = c.get_info("status/bootstrap-phase")
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

    if callable(tor_status_update_func):
        if not tor_status_update_func(progress, summary):
            # If the dialog was canceled, stop connecting to Tor
            common.log(
                "Onion",
                "connect",
                "tor_status_update_func returned false, canceling connecting to Tor",
            )
            print()
            return False

    if summary == "Done":
        print("")
        break
    time.sleep(0.2)