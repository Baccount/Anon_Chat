# trunk-ignore(flake8/E402)
from server.server_tor import CreateOnion




class TestStartServer():

    def setup_method(self):
        self.onion = CreateOnion()

    # test if ephemeral_onion is created
    def test_ephemeral_onion(self):
        address = self.onion.ephemeral_onion()
        # check if the address is 56 characters long
        assert len(address.service_id) == 56

    # test if non_ephemeral_onion is created
    def test_non_ephemeral_onion(self):
        address = self.onion.non_ephemeral_onion()
        # check if the address is 56 characters long
        assert len(address.service_id) == 56