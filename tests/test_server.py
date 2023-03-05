import sys
sys.path.append('../')

# trunk-ignore(flake8/E402)
from server.server_tor import CreateOnion



# run tests for client
def test_server_tor():
    # test tor connection
    pass

if __name__ == "__main__":
    test_server_tor()