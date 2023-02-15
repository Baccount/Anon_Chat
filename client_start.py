from client.client import Client
import os
import subprocess
from time import sleep
import psutil

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

# check if tor is running and start if not

try:
    subprocess.check_output(['which', 'tor'])
except subprocess.CalledProcessError:
    print('Tor is not installed')
    os.system("brew install tor")

# Check if Tor is running
for proc in psutil.process_iter():
    if proc.name() == 'tor':
        print('Tor is running')
        break
else:
    print('Tor is not running')
    os.system("brew services restart tor")
    sleep(5)


client = Client()
client.start()
