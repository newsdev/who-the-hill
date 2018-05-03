import logging
import json
import os
import re

def export2env():
    """
    For local development.
    """
    CREDS_FILE = os.environ.get('CREDS_FILE', 'staging-credentials.json')
    with open(, 'r') as readfile:
        creds = json.loads(readfile.read())

        for k,v in creds.items():
            os.system('export %s="%s"' % (k.replace('-', '_').upper(), v))
            print('export %s="%s"' % (k.replace('-', '_').upper(), v))

def valid_uuid(possible_uuid):
    """
    Checks that a possible UUID4 string is a valid UUID4.
    """
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(possible_uuid)
    return bool(match)

def clean_payload(payload):
    """
    Serializes a payload from form strings to more useful Python types.
    `payload` is a dictionary where both keys and values are exclusively strings.
    * empty string becomes None
    * applies a true / false test to possible true / false string values.
    """
    output = {}
    for k,v in payload.items():

        # Takes the first value.
        v = v[0]

        # Serializes values
        if v == u'':
            v = None
        if v.lower() in ['true', 'yes', 'y', '1']:
            v = True
        if v.lower() in ['false', 'no', 'n', '0']:
            v = False

        # Values not in the test pass through.
        output[k] = v
    return output

def get_env():
    return os.environ.get('DEPLOYMENT_ENVIRONMENT', 'dev')

class HealthcheckFilter(logging.Filter):
    def filter(self, log_record):
        if 'healthcheck' in log_record.msg:
            return False
        return True

def setup_logging():
    """
    To be invoked by settings.
    """
    log = logging.getLogger('werkzeug')

    log.addFilter(HealthcheckFilter())
    log.setLevel(logging.INFO)

    logging.basicConfig(level=logging.INFO)

    return log