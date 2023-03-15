from json import dump
from logging_msgs import log_msg





def saveBridges(bridge_lst):
    """
    Save the bridges to a file
    """
    log_msg("StartServer", "saveBridges", "Saving bridges to bridges.json")
    # write the bridges from the file
    with open("bridges.json", "w") as f:
        dump(bridge_lst, f)