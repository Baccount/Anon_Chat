from bridges.downloadbridges import DownloadBridges
import json

def main():
    db = DownloadBridges()
    db.getCaptcha()
    db.display_image()
    if not db.checkCaptcha():
        print("Captcha is incorrect")
        main()
    db.saveBridges()
    db.cleanup()
    
    print("bridges saved to bridges.json")
    with open('bridges.json', 'r') as f:
        my_list = json.load(f)
    print(my_list[0])

if __name__ == "__main__":
    main()