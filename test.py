from bridges.downloadbridges import DownloadBridges

def main():
    db = DownloadBridges()
    db.getCaptcha()

    db.display_image()
    db.checkCaptcha()
    bridges = db.getBridges()
    print(bridges)
    db.cleanup()

if __name__ == "__main__":
    main()