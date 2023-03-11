import subprocess
from logging_msg import log_msg

def force_kill_tor():
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