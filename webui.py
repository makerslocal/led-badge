from snapconnect import snap
from flask import Flask, request
from time import sleep
import threading

SERIAL_TYPE = snap.SERIAL_TYPE_RS232
SERIAL_PORT = "/dev/ttyUSB0"

class BadgeClient(object):
    def __init__(self):
        self.comm = snap.Snap(funcs={})
        self.comm.open_serial(SERIAL_TYPE, SERIAL_PORT)

    def send_color(self, red, green, blue):
        self.comm.mcast_rpc(1, 5, 'receive_color', red, green, blue)

client = BadgeClient()
app = Flask(__name__)

@app.route('/color', methods=['PUT'])
def set_color():
    color = request.form['color'].lower()
    if color == "orange":
        client.send_color(True, True, False)
    elif color == "yellow":
        client.send_color(True, True, True)
    elif color == "red":
        client.send_color(True, False, False)
    elif color == "purple":
        client.send_color(True, False, True)
    elif color == "blue":
        client.send_color(False, False, True)
    elif color == "green":
        client.send_color(False, True, False)

    return "Ok"

def run_jobs():
    while True:
        client.comm.poll()
        sleep(0.1)

thread = threading.Thread(target=run_jobs)
thread.start()

app.run()

