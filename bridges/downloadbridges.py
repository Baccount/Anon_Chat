from .meek import Meek
import requests
from logging_msg import log_msg
import os
import base64
import io
import matplotlib.pyplot as plt
from PIL import Image
import json


class DownloadBridges:
    def __init__(self):
        self.meek_path = os.path.join(os.path.dirname(__file__), "meek-client")
        log_msg("DownloadBridges", "__init__", "Meek path: " + self.meek_path)

        self.meek = Meek(self.meek_path)
        self.meek_proxies = self.meek.start()
        log_msg("DownloadBridges", "__init__", f"Meek Proxie: {self.meek_proxies}")
        
        # cleanup meek when the program exits
        import atexit
        atexit.register(self.meek.cleanup)




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
                            "supported": ["obfs4", "snowflake"],
                        }
                    ]
                },
            )
            moat_res = captcha.json()
            self.transport = moat_res["data"][0]["transport"]
            self.image = moat_res["data"][0]["image"]
            self.challenge = moat_res["data"][0]["challenge"]
        except Exception as e:
            log_msg("DownloadBridges", "getBridge", f"Error: {e}")

    def display_image(self):

        # Handle window closing event
        def on_close(event):
            plt.close()

        img_data = self.image
        # Convert Base64 data to image
        img_bytes = base64.b64decode(img_data)
        img = Image.open(io.BytesIO(img_bytes))
        fig, ax = plt.subplots()
        ax.imshow(img)
        fig.canvas.mpl_connect('close_event', on_close)
        # Show the Matplotlib figure without blocking
        plt.show(block=False)



    def checkCaptcha(self):
        """
        Check the Captcha and return True if it is correct
        """
        try:
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
            log_msg("display_image","on_close", "Closing the window")
            plt.close()
        except Exception as e:
            log_msg("DownloadBridges", "checkCaptcha", "Error: " + str(e))
            return False
        # If data is present, then the captcha is correct
        try:
            data = self.bridge.json()["data"]
            if not data:
                log_msg("DownloadBridges", "checkCaptcha", "Error: ")
                return False
        except Exception as e:
            log_msg("DownloadBridges", "checkCaptcha", "Error: " + str(e))
            return False
        log_msg("DownloadBridges","checkCaptcha",  "Captcha is correct")
        log_msg("Bridges", data)
        return True

    def getBridges(self):
        """
        Return the bridges
        """
        bridges = []
        for item in self.bridge.json()['data']:
            bridges.extend(item['bridges'])
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
        with open('bridges.json', 'w') as f:
            json.dump(bridge_lst, f)
