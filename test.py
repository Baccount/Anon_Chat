from bridges.downloadbridges import DownloadBridges


def main():
    db = DownloadBridges()
    db.getCaptcha()
    db.display_image()
    if not db.checkCaptcha():
        print("Captcha is incorrect")
        main()
    db.saveBridges()
    db.cleanup()
    obsf4Bridges = db.readBridges()
    print(obsf4Bridges)


if __name__ == "__main__":
    main()
