from flask import Flask, request, Response, jsonify
import boto3
import botocore
import base64
import logging
from log_filter import HealthcheckFilter

app = Flask(__name__)

healthcheck_filter = HealthcheckFilter()
log = logging.getLogger('werkzeug')
log.addFilter(healthcheck_filter)
log.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

client = boto3.client('rekognition')

@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    '''
    Checks that the app is properly running.
    '''
    return 'shazongress'

@app.route('/recognize', methods=["POST"])
def recongize():
    '''
    Receives POST request from Twilio. Sends data from request to Amazon Rekognize and receives the API's analysis.
    Returns the resulting analysis as JSON.
    '''
    # Reads image data from incoming request
    r = request
    data = r.files['file'].read()

    # Sends image data to Amazon Rekognize for analysis. Returns JSON response of results.
    try:
        results = client.recognize_celebrities(Image={'Bytes': data})
    except botocore.exceptions.ClientError as e:
        results = {"Rekognition Client Error": str(e)}
    logging.info(results)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)