from client.client import Client
#from download_tor import start

# downlaod to support work in progress

#start("macos")














try:
    client = Client()
    client.start()
except KeyboardInterrupt:
    # clear the terminal screen
    print('\033[2J')
    exit(0)
