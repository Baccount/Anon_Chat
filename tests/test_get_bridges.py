import sys
from os import getenv

import pytest

sys.path.append("../")
# trunk-ignore(flake8/E402)
from bridges.downloadbridges import DownloadBridges


@pytest.mark.skipif(
    getenv("GITHUB_ACTIONS") == "true", reason="Skipping test on GitHub Actions Because meek-client is not supported on GitHub Actions 'Linux does not support it'."
)
class TestDownloadBridges:
    def setup(self):
        self.db = DownloadBridges(protocol="obfs4", test=True)
        # test connect Meek
        assert self.db.connectMeek() is True

    def test_getCaptcha(self):
        assert self.db.getCaptcha() is True

    def test_display_image(self):
        assert self.db.display_image() is True

    def test_cleanup(self):
        assert self.db.cleanup() is True

    def test_check_data(self):
        # test checkData
        data = {
            "data": [
                {
                    "version": "0.1.0",
                    "type": "client-transports",
                    "supported": ["obfs4"],
                }
            ]
        }
        assert self.db.checkData(data) is True
