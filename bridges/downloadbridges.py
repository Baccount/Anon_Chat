import base64
import io
import json
import os
import requests
from PIL import Image
from logging_msg import log_msg
from .meek import Meek



class DownloadBridges:
    def __init__(self):
        self.connectMeek()

    def connectMeek(self):
        self.meek_path = os.path.join(os.path.dirname(__file__), "meek-client")
        log_msg("DownloadBridges", "__init__", "Meek path: " + self.meek_path)

        self.meek = Meek(self.meek_path)
        self.meek_proxies = self.meek.start()
        log_msg("DownloadBridges", "__init__", f"Meek Proxie: {self.meek_proxies}")

    def getCaptcha(self):
        try:
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
                            "supported": ["obfs4"],
                        }
                    ]
                },
            )
            moat_res = captcha.json()
            self.transport = moat_res["data"][0]["transport"]
            self.image = moat_res["data"][0]["image"]
            self.challenge = moat_res["data"][0]["challenge"]
            log_msg("getCaptcha", "getBridge", f"Transport: {self.transport}")
        except Exception as e:
            log_msg("DownloadBridges", "getBridge", f"Error: {e}")

    def display_image(self):
        try:
            base64_image_data = self.image
            image_data = base64.b64decode(base64_image_data)
            image = Image.open(io.BytesIO(image_data))
            image.show()
        except Exception as e:
            log_msg("DownloadBridges", "display_image", f"Error: {e}")

    def checkCaptcha(self):
        """
        Check the Captcha and return True if it is correct
        """
        try:
            log_msg("DownloadBridges", "checkCaptcha", "Checking Captcha")
            solution = input("Enter the solution: ")
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
                            "solution": solution,
                            "qrcode": "false",
                        }
                    ]
                },
            )
            if self.bridge.status_code != 200:
                log_msg(self.red("DownloadBridges"), self.red("checkCaptcha", "Server Error: " + str(self.bridge.status_code)))
                return False
        except Exception as e:
            log_msg("DownloadBridges", "checkCaptcha", "Error: " + str(e))
            return False
        return self.checkData()


    def checkData(self):
        """ Check the data

        Returns:
            bool: True if it exists else False
        """
        try:
            data = self.bridge.json()["data"]
            if not data:
                log_msg("DownloadBridges", "checkCaptcha", "Captcha is incorrect")
                return False
        except Exception as e:
            log_msg("DownloadBridges", "checkCaptcha", "Error: " + str(e))
            return False
        # Success
        log_msg("DownloadBridges", "checkCaptcha", "Captcha is correct")
        log_msg("Bridges", data)
        return True

    def getBridges(self):
        """
        Return the bridges
        """
        bridges = []
        for item in self.bridge.json()["data"]:
            bridges.extend(item["bridges"])
        return bridges

    def cleanup(self):
        """
        Cleanup the meek process
        """
        self.meek.cleanup()

    def saveBridges(self):
        """
        Save the bridges to a file
        """
        log_msg("DownloadBridges", "saveBridges", "Saving bridges to bridges.json")
        bridge_lst = self.getBridges()
        with open("bridges.json", "w") as f:
            json.dump(bridge_lst, f)

    def readBridges(self):
        """
        Read the bridges from a file
        """
        log_msg("DownloadBridges", "readBridges", "Reading bridges from bridges.json")
        with open("bridges.json", "r") as f:
            my_list = json.load(f)
        return my_list

# accecp any number of arguments
    def red(self, *args):
        return f"\033[91m {args}\033[00m"
