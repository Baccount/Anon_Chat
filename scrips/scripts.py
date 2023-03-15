from json import dump
from logging_msg import log_msg
from colorama import Fore, Style




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