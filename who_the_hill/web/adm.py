import base64
import logging
import os

from flask import Flask, request, Response, jsonify, render_template

app = Flask(__name__)

@app.route('/', methods=["GET"])
def index():
    return render_template('who_the_hill/templates/index.html', number=os.environ.get('TWILIO_NUMBER', None))

@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    '''
    Checks that the app is properly running.
    '''
    return '200 ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)