# app.py
# Rohan Weeden
# Created: Feb. 2. 2018

# Flask server for displaying the hosts that are up on the given subnet

from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def index():
    return 'test'


if __name__ == '__main__':
    app.debug = True
    app.run()
