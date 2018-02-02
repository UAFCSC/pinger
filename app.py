# app.py
# Rohan Weeden
# Created: Feb. 2. 2018

# Flask server for displaying the hosts that are up on the given subnet

import atexit
from flask import Flask
from flask import render_template
from threading import Timer, Thread, Lock
from time import time

app = Flask(__name__)


ping_thread = Thread()
lock = Lock()

PING_TIME = 5 # Seconds


@app.route('/')
def index():
    return render_template('show_active.html')


def ping_subnet():
    global ping_thread
    global lock

    with lock:
        print("got lock")
        pass

    ping_thread = Timer(PING_TIME, ping_subnet)
    ping_thread.start()


def interrupt():
    global ping_thread
    ping_thread.cancel()


if __name__ == '__main__':
    ping_thread = Timer(PING_TIME, ping_subnet)
    ping_thread.start()

    atexit.register(interrupt)

    # Debug causes extra threads to run
    # app.debug = True
    app.run()
