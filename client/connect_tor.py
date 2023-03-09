import socks
import socket
import subprocess
from logging_msg import log_msg

class ConnectTor(object):

    def __init__(self, test=False):
        self.test = test
        try:
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            log_msg("CreateOnion", "__init__", f"Error: {e}")
            self.force_kill_tor()
            exit(1)

    def force_kill_tor(self):
        """
        Force kill the tor process
        """
        try:
            log_msg("force_kill_tor", "Killing tor subprocess")
            # Find the process IDs (PIDs) of the processes with the given name
            pid_command = ["pgrep", "-x", "tor"]
            pid_process = subprocess.Popen(pid_command, stdout=subprocess.PIPE)
            pid_output, _ = pid_process.communicate()
            pids = pid_output.decode().strip().split("\n")
            # Kill each process with the found PIDs
            if pids:
                for pid in pids:
                    kill_command = ["kill", pid]
                    subprocess.run(kill_command)
                    print(f"Process tor (PID {pid}) killed.")
            else:
                print("No process named tor found.")

        except Exception as e:
            print(e)

    def connect_onion(self, onion):
        log_msg("connect_tor", "connect_onion", f"connecting to {onion}")
        self.server = (onion, 80)
        self.socket.connect(self.server)
        if self.test:
            # were testing
            return True