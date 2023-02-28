from downloadBridges.meek import Meek
import requests
import logging_msg as log
import os


def main():
    meek_path = os.path.join(os.path.dirname(__file__), "tor", "meek-client")
    meek = Meek(meek_path)
    meek_proxies = meek.start()

# Request a bridge
    r = requests.post(
        "https://bridges.torproject.org/moat/fetch",
        headers={"Content-Type": "application/vnd.api+json"},
        proxies=meek_proxies,
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
    moat_res = r.json()
    transport = moat_res["data"][0]["transport"]
    image = moat_res["data"][0]["image"]
    challenge = moat_res["data"][0]["challenge"]
    
    # render base64 image to png
    import base64
    with open("bridge.png", "wb") as fh:
        fh.write(base64.b64decode(image))
        
    
    
    
    # Check the CAPTCHA
    r = requests.post(
        "https://bridges.torproject.org/moat/check",
        headers={"Content-Type": "application/vnd.api+json"},
        proxies=meek_proxies,
        json={
            "data": [
                {
                    "id": "2",
                    "type": "moat-solution",
                    "version": "0.1.0",
                    "transport": transport,
                    "challenge": challenge,
                    "solution": input("Enter the solution: "),
                    "qrcode": "false",
                }
            ]
        },
    )
    bridges = []
    for item in r.json()['data']:
        bridges.extend(item['bridges'])
    print(bridges)




if __name__ == "__main__":
    main()