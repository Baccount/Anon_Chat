import sys
sys.path.append('../')

# trunk-ignore(flake8/E402)
from bridges.downloadbridges import DownloadBridges






class TestDownloadBridges():
    def setup(self):
        self.db = DownloadBridges(protocol="obfs4", test=True)
    
    
    def test_connectMeek(self):
        assert self.db.connectMeek() is True
    
    def test_getCaptcha(self):
        assert self.db.getCaptcha() is True
        # db.saveBridges()
        # db.cleanup()
        # obsf4Bridges = db.readBridges()