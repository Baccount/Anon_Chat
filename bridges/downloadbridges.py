from .meek import Meek
import requests
from logging_msg import log_msg
import os



class DownloadBridges:
    def __init__(self):
        self.meek_path = os.path.join(os.path.dirname(__file__), "meek-client")
        log_msg("DownloadBridges", "__init__", "Meek path: " + self.meek_path)

        self.meek = Meek(self.meek_path)
        self.meek_proxies = self.meek.start()
        log_msg("DownloadBridges", "__init__", f"Meek Proxie: {self.meek_proxies}")




    def getCaptcha(self):
        log_msg("DownloadBridges", "getBridge", "Getting bridge")
        captcha = requests.post(
            "https://bridges.torproject.org/moat/fetch",
            headers={"Content-Type": "application/vnd.api+json"},
            proxies=self.meek_proxies,
            json={
                "data": [
                    {
                        "version": "0.1.0",
                        "type": "client-transports",
                        "supported": ["obfs4", "snowflake"],
                    }
                ]
            },
        )
        moat_res = captcha.json()
        self.transport = moat_res["data"][0]["transport"]
        image = moat_res["data"][0]["image"]
        self.challenge = moat_res["data"][0]["challenge"]

        # render base64 image to png
        import base64
        with open("bridge.png", "wb") as fh:
            fh.write(base64.b64decode(image))




    def checkCaptcha(self):
        """
        Check the Captcha and return True if it is correct
        """
        log_msg("DownloadBridges", "checkCaptcha", "Checking Captcha")
        self.bridge = requests.post(
            "https://bridges.torproject.org/moat/check",
            headers={"Content-Type": "application/vnd.api+json"},
            proxies=self.meek_proxies,
            json={
                "data": [
                    {
                        "id": "2",
                        "type": "moat-solution",
                        "version": "0.1.0",
                        "transport": self.transport,
                        "challenge": self.challenge,
                        "solution": input("Enter the solution: "),
                        "qrcode": "false",
                    }
                ]
            },
        )

    def getBridges(self):
        """
        Return the bridges
        """
        bridges = []
        for item in self.bridge.json()['data']:
            bridges.extend(item['bridges'])
        return bridges