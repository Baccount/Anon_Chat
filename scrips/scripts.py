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