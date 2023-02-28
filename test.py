from bridges.downloadbridges import DownloadBridges

def main():
    db = DownloadBridges()
    db.getCaptcha()
    db.display_image()
    if not db.checkCaptcha():
        print("Captcha is incorrect")
        main()
    bridges = db.getBridges()
    print(bridges)
    db.cleanup()

if __name__ == "__main__":
    main()