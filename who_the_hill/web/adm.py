import base64
import importlib
import logging
import os

from flask import Flask, request, Response, jsonify, render_template

from who_the_hill import utils

settings = importlib.import_module('config.%s.settings' % utils.get_env())
app = Flask(__name__, template_folder=settings.TEMPLATE_PATH)

@app.route('/', methods=["GET"])
def index():
    return render_template('index.html', number=os.environ.get('TWILIO_NUMBER', None))

@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    '''
    Checks that the app is properly running.
    '''
    return '200 ok'

if __name__ == '__main__':
    TEMPLATE_PATH = '%s/templates/' % os.path.dirname(os.path.realpath(__file__))
    app.run(host='0.0.0.0', port=8888, debug=True)