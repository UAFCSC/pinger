# app.py
# Rohan Weeden
# Created: Feb. 2. 2018

# Flask server for displaying the hosts that are up on the given subnet

import atexit
from flask import Flask
from flask import render_template, request
from flask_socketio import SocketIO
from threading import Timer, Thread, Lock
from time import time

app = Flask(__name__)
socketio = SocketIO(app)

detected_ips = []
ip_names = {
    "0.0.0.0" : "Thats not a real ip"
}
ping_thread = Thread()
lock = Lock()

PING_TIME = 2 # Seconds


@app.route('/')
def index():
    global detected_ips, ip_names
    with lock:
        return render_template('show_active.html', ips=detected_ips, names=ip_names)


@app.route('/set_nickname', methods=['GET', 'POST'])
def set_nickname():
    if request.method == 'POST':
        ip = request.form.get('ip')
        name = request.form.get('name')
        error = True
        if ip is not None and name is not None:
            global ip_names
            ip_names[ip] = name
            error = False

        socketio.emit('new_ips', [(ip, ip_names.get(ip)) for ip in detected_ips])
        return render_template('set_nickname.html', submitted=True, error=error)

    return render_template('set_nickname.html')


def ping_subnet():
    global ping_thread
    global detected_ips
    global ip_names
    global lock
    global socketio

    with lock:
        ip = '0.0.0.0'
        detected_ips.append(ip)
        socketio.emit('new_ips', [(ip, ip_names.get(ip)) for ip in detected_ips])

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
    socketio.run(app)
