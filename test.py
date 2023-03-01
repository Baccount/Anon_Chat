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
    
    print(db.readBridges())

if __name__ == "__main__":
    main()