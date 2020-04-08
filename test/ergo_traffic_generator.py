import time
import random
import threading

import requests

endpoints = ('device', 'device/devices', 'measurements', 'measurements/0/0/1', 'error')


def run():
    while True:
        try:
            target = random.choice(endpoints)
            requests.get("http://<ERGO_API_SERVICE_IP>:5000/api/v1/%s" % target, timeout=1)
        except:
            pass


if __name__ == '__main__':
    for _ in range(4):
        thread = threading.Thread(target=run)
        thread.setDaemon(True)
        thread.start()

    while True:
        time.sleep(1)
