# app.py
# Rohan Weeden
# Created: Feb. 2. 2018

# Flask server for displaying the hosts that are up on the given subnet

import atexit
import ipaddress
from flask import Flask
from flask import render_template, request
from flask_socketio import SocketIO
from threading import Timer, Thread, Lock
from time import time
import subprocess
import sys

app = Flask(__name__)
socketio = SocketIO(app)

ip_net = None
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
    global ip_net

    ips = []
    for host in ip_net.hosts():
        output = subprocess.Popen(
            ['fping', '-c1', '-t50', str(host)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output.communicate()[0]
        if output.returncode == 0:
            ips.append(str(host))
    with lock:
        detected_ips = ips
        print(detected_ips)
        socketio.emit('new_ips', [(ip, ip_names.get(ip)) for ip in detected_ips])

    ping_thread = Timer(PING_TIME, ping_subnet)
    ping_thread.start()


def interrupt():
    global ping_thread
    ping_thread.cancel()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Must supply a subnet to monitor.")
        print("app.py 10.250.100.1.0/24")
        sys.exit()

    try:
        ip_net = ipaddress.ip_network(sys.argv[1])
    except ValueError as e:
        print(e)
        sys.exit()

    ping_thread = Timer(PING_TIME, ping_subnet)
    ping_thread.start()

    atexit.register(interrupt)

    # Debug causes extra threads to run
    # app.debug = True
    socketio.run(app)
