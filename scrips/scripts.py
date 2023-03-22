from json import dump
from logging_msg import log_msg
from colorama import Fore, Style
from subprocess import Popen, PIPE, run




def saveBridges(bridge_lst):
    """
    Save the bridges to a file
    """
    log_msg("StartServer", "saveBridges", "Saving bridges to bridges.json")
    # write the bridges from the file
    with open("bridges.json", "w") as f:
        dump(bridge_lst, f)

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        # print the line and clear it
        final_msg = f"{Fore.WHITE + Style.DIM}{line}{Style.RESET_ALL}"
        print(final_msg, end="\r")

def ascii_client():
    print(
        """
           d8888                             .d8888b.  888               888    
          d88888                            d88P  Y88b 888               888    
         d88P888                            888    888 888               888    
        d88P 888 88888b.   .d88b.  88888b.  888        88888b.   8888b.  888888 
       d88P  888 888 "88b d88""88b 888 "88b 888        888 "88b     "88b 888    
      d88P   888 888  888 888  888 888  888 888    888 888  888 .d888888 888    
     d8888888888 888  888 Y88..88P 888  888 Y88b  d88P 888  888 888  888 Y88b.  
    d88P     888 888  888  "Y88P"  888  888  "Y8888P"  888  888 "Y888888  "Y888 \n"""
    )


def server_ascii():
    print(
        """
           d8888                             .d8888b.  888               888          .d8888b.                                             
          d88888                            d88P  Y88b 888               888         d88P  Y88b                                            
         d88P888                            888    888 888               888         Y88b.                                                 
        d88P 888 88888b.   .d88b.  88888b.  888        88888b.   8888b.  888888       "Y888b.    .d88b.  888d888 888  888  .d88b.  888d888 
       d88P  888 888 "88b d88""88b 888 "88b 888        888 "88b     "88b 888             "Y88b. d8P  Y8b 888P"   888  888 d8P  Y8b 888P"   
      d88P   888 888  888 888  888 888  888 888    888 888  888 .d888888 888               "888 88888888 888     Y88  88P 88888888 888     
     d8888888888 888  888 Y88..88P 888  888 Y88b  d88P 888  888 888  888 Y88b.       Y88b  d88P Y8b.     888      Y8bd8P  Y8b.     888     
    d88P     888 888  888  "Y88P"  888  888  "Y8888P"  888  888 "Y888888  "Y888       "Y8888P"   "Y8888  888       Y88P    "Y8888  888     
        """
    )

def force_kill_tor():
    """
    Force kill the tor process
    """
    try:
        log_msg("force_kill_tor", "Killing tor subprocess")
        # Find the process IDs (PIDs) of the processes with the given name
        pid_command = ["pgrep", "-x", "tor"]
        pid_process = Popen(pid_command, stdout=PIPE)
        pid_output, _ = pid_process.communicate()
        pids = pid_output.decode().strip().split("\n")
        # Kill each process with the found PIDs
        if pids:
            for pid in pids:
                kill_command = ["kill", pid]
                run(kill_command)
                print(f"Process tor (PID {pid}) killed.")
        else:
            print("No process named tor found.")
    except Exception as e:
        print(e)

def decode(buffer):
    """
    Decode the buffer into individual JSON objects.

    :param buffer: The buffer to be decoded.
    :return: A list of JSON objects.
    """
    objects = []
    start = 0
    end = buffer.find("{", start)
    while end != -1:
        start = end
        count = 1
        end = start + 1
        while count > 0 and end < len(buffer):
            if buffer[end] == "{":
                count += 1
            elif buffer[end] == "}":
                count -= 1
            end += 1
        objects.append(buffer[start:end])
        start = end
        end = buffer.find("{", start)
    return objects


def g(text):
    # return green text
    return "\033[92m" + text + "\033[0m"

def r(msg):
    # return red text
    return f"\033[31m{msg}\033[0m"
