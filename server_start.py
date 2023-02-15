from server.server import Server
import os
import subprocess

# check if brew is installed and install if not on mac
try:
    subprocess.check_output(['brew', '--version'])
except subprocess.CalledProcessError:
    print("Brew is not installed, installing now...")
    os.system("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")


try:
    subprocess.check_output(['which', 'tor'])
except subprocess.CalledProcessError:
    print('Tor is not installed')
    os.system("brew install tor")

# start tor service using brew and print the status
os.system("brew services restart tor")

server = Server()
server.start()
