from bridges.downloadbridges import DownloadBridges
def main():
    db = DownloadBridges()
    db.getCaptcha()
    db.checkCaptcha()
    bridges = db.getBridges()
    print(bridges)

if __name__ == "__main__":
    main()