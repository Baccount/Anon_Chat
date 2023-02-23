import time
from colorama import Fore, Style



verbose = True

def log_msg(module, func, msg=None):
    """
    If verbose mode is on, log error messages to stdout
    """
    if verbose:
        timestamp = time.strftime("%b %d %Y %X")
        final_msg = f"{Fore.LIGHTBLACK_EX + Style.DIM}[{timestamp}]{Style.RESET_ALL} {Fore.WHITE + Style.DIM}{module}.{func}{Style.RESET_ALL}"
        if msg:
            final_msg = (
                f"{final_msg}{Fore.WHITE + Style.DIM}: {msg}{Style.RESET_ALL}"
            )
        print(final_msg)