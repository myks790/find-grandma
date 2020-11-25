import requests
import config
import time
import random
import threading


def _save(base_path):
    r = requests.get(config.snapshotHost + "&q=0&d=1&rand=" + str(random.random()))
    filename = time.strftime("%m_%d %H-%M-%S") + ".jpg"
    file = open(base_path+"/snapshots/" + filename, "wb")
    file.write(r.content)
    file.close()


def snapshot_down(base_path):
    threading.Timer(1, _save, args=(base_path,)).start()