import requests
import config
import time
import random
import threading


def _save(base_path):
    try:
        r = requests.get(config.snapshot_host + "&q=0&d=1&rand=" + str(random.random()), timeout=10)
        filename = time.strftime("%m_%d %H-%M-%S") + ".jpg"
        file = open(base_path+"/snapshots/" + filename, "wb")
        file.write(r.content)
        file.close()
    finally:
        threading.Timer(1, _save, args=(base_path,)).start()


def snapshot_down(base_path):
    _save(base_path)
