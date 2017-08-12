from flask import Flask, request, Response, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import urllib
from io import BytesIO
import requests
import json
from PIL import Image, ImageDraw
import os
import boto3
import uuid
import psycopg2
import alerter
from log_filter import HealthcheckFilter
import logging
from image import Image as RecognitionImage
from rekognitionrecognizer import RekognitionRecognizer
from face import Face

app = Flask(__name__)
healthcheck_filter = HealthcheckFilter()
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addFilter(healthcheck_filter)
logging.basicConfig(level=logging.INFO)

s3 = boto3.resource(
    's3',
    endpoint_url=os.environ['AWS_S3_ENDPOINT'],
    aws_access_key_id=os.environ['AWS_GCS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_GCS_SECRET_ACCESS_KEY'],
)
twilio_client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

recognizer = RekognitionRecognizer(os.environ['FACIAL_RECOGNITION_ENDPOINT'])

failure_message = 'No member recognized, sorry'
confidence_levels = [
    {"prob": 95.0, "description": "almost certainly"},
    {"prob": 90.0, "description": "highly likely"}, 
    {"prob": 80.0, "description": "good chance"}, 
    {"prob": 70.0, "description": "likely"},
    {"prob": 60.0, "description": "possible"}, 
    {"prob": 20.0, "description": "unlikely"}, 
    {"prob": 0.0, "description": "highly unlikely"}
]

rectangle_width = 5
rectangle_colors = [
    "red",
    "blue",
    "green",
    "purple",
    "cyan",
    "orange",
    "black",
    "white"
]

def get_nicknames(nickname_env_var, local_filename):
    '''
    Gets a mapping of nicknames to names.
    If there's an api endpoint supplied in the environment variables, it uses that.
    Else the function returns names from a local file
    '''
    nicknames_endpoint = os.getenv(nickname_env_var)
    if nicknames_endpoint is not None:
        logging.info("loading nicknames from endpoint...")
        response = requests.get(nicknames_endpoint)
        return response.json()
    else:
        logging.info("loading nicknames from json dump...")
        with open(local_filename, 'r', encoding="utf8") as f:
            nicknames = json.loads(f.read())
            return nicknames
    return []

logging.info("Downloading nicknames...")
nicknames = get_nicknames('NICKNAMES_ENDPOINT', 'nicknames_dump.json')
logging.info("Nicknames downloaded")

def get_doppelgangers(doppelganger_filename):
    with open(doppelganger_filename, 'r') as f:
        return json.loads(f.read())

doppelgangers = get_doppelgangers('doppelgangers.json')

def getRecipients():
    ''' Fetch email recipients from environment variable. '''
    emails = os.environ["EMAIL_RECIPIENTS"]
    emails = emails.split(" ")
    return emails

MY_ALERT = alerter.Alerter(counter_limit=100, time_interval=3600, recipients=getRecipients())

@app.route('/', methods=["GET"])
def info_page():
    '''
    returns an info page for Shazongress
    '''
    return render_template("info_page.html", number=os.environ['TWILIO_NUMBER'], app_name=os.environ['APP_NAME'])


@app.route('/healthcheck', methods=["GET"])
def healthcheck():
    '''
    Checks that the app is properly running.
    '''
    return "Hello!"

@app.route('/recognize', methods=["POST"])
def recongize():
    '''
    Fetches image from incoming text message. Sends image to app.py (Amazon Rekognition) for analysis.
    Sends reply text message.
    '''
    logging.info("MESSAGE RECIEVED")
    # Checks if application is being hit too many times per time interval.
    # If so, send an email alert.
    MY_ALERT.abuse_check()

    # Fetches image url from Twilio request object
    media_url = request.values.get('MediaUrl0')
    logging.info(media_url)

    # Fetches incoming phone number
    external_num = request.values.get('From')
    logging.info("From: " + external_num)

    # Fetches twilio phone number
    twilio_num = request.values.get('To')
    logging.info("Twilio number: " + twilio_num)

    # Create image object from image url
    target_image = RecognitionImage(image_url=media_url)
    
    try:
        # Makes POST request with image to app.py on port 8888
        logging.info("Sending image to rekognition app...")
        #r = requests.post(os.environ['FACIAL_RECOGNITION_ENDPOINT'], files={'file': f.getvalue()})
        recognizer.recognize(target_image)

        # Sends reply text based on content in Amazon Rekognition's response
        resp = MessagingResponse()
        #face_obj = json.loads(r.text)
        #if ("CelebrityFaces" in face_obj and len(face_obj['CelebrityFaces']) > 0):
        if len(target_image.recognized_faces) > 0:
            #face_messages = process_faces(face_obj['CelebrityFaces'], f)
            face_messages = process_faces(target_image)
            if len(face_messages) == 0:
                resp.message(failure_message)
                del target_image
                return str(resp)
            key_str = 'faces/' + str(uuid.uuid4()) + '.png'
            target_image.get_image_file().seek(0)
            bucket_folder_name = 'who-the-hill'
            s3.Bucket(bucket_folder_name).put_object(Key=key_str, Body=target_image.get_image_file(), ContentType='image/png')
            url = os.environ['AWS_S3_ENDPOINT'] + "/" + bucket_folder_name + "/" + key_str
            logging.info("Image uploaded to: " + url)
            logging.info("\n".join(face_messages))
            resp.message("\n".join(face_messages))
            message = twilio_client.messages.create(
                to=external_num,
                from_=twilio_num,
                media_url=url)
        else:
            logging.info("Failure message sent")
            resp.message(failure_message)
    finally:
        del target_image
        
    return str(resp)

def process_faces(image):
    ''' Calls methods to draw boxes around faces and generate response messages for faces '''
    logging.debug([x.name for x in image.recognized_faces])
    filtered_objs = [x for x in image.recognized_faces if findCongressPerson(x.name, nicknames)]

    # We're adding back in doppelgangers after filtering so that in case the name of the
    # member of Congress in the doppelgangers file is slightly different from the name in
    # the endpoint/json dump, it'll still be included in the results. Basically, this
    # makes it so that we're not dependent on the exact spellings in the doppelgangers file
    for obj in image.recognized_faces:
        if obj not in filtered_objs and obj.name in doppelgangers:
            logging.info("DOPPELGANGER: {}, {}".format(obj.name, doppelgangers[obj.name]))
            obj.name = doppelgangers[obj.name]
            filtered_objs.append(obj)
    colors = draw_bounding_boxes(filtered_objs, image.get_image_file())
    return [generate_message(x, color) for x, color in zip(filtered_objs, colors)]

def generate_message(celeb_obj, color):
    ''' Generates a response message for a celebrity recognition object recieved from Amazon Rekognition '''
    name = celeb_obj.name
    confidence = float(celeb_obj.confidence)
    description = "highly unlikely"
    for level in confidence_levels:
        if confidence >= level['prob']:
            description = level['description']
            break
    
    result  = "{} ({}, {} - confidence = {})".format(name, color, description, confidence)
    return result

def draw_width_rectangle(drawing, coordinates, color, width, fill=None):
    '''
    Draws a rectangle of an inputted width using the PIL drawing object
    '''
    for i in range(width):
        x0 = coordinates[0] - i
        y0 = coordinates[1] - i
        x1 = coordinates[2] + i
        y1 = coordinates[3] + i
        drawing.rectangle([x0, y0, x1, y1], outline=color)

def draw_bounding_boxes(celeb_objs, file):
    '''
    Draws bounding boxes around all faces in inputted file determined by celeb_objs
    '''
    colors = []
    im = Image.open(file)
    draw = ImageDraw.Draw(im)
    for i in range(len(celeb_objs)):
        color = rectangle_colors[i % len(rectangle_colors)]
        colors.append(color)
        coords = get_coords_from_ratios(celeb_objs[i].to_dict()['BoundingBox'], im.width, im.height)
        draw_width_rectangle(draw, coords, color, rectangle_width)
    
    del draw
    file.seek(0)
    im.save(file, 'PNG')
    return colors

def get_coords_from_ratios(bounding_box_ratios, img_width, img_height):
    ''' Calculate face-box coordinates from passed-in ratios and image size. '''
    x0 = int(bounding_box_ratios['Left'] * float(img_width))
    y0 = int(bounding_box_ratios['Top'] * float(img_height))
    x1 = x0 + int(bounding_box_ratios['Width'] * float(img_width))
    y1 = y0 + int(bounding_box_ratios['Height'] * float(img_height))
    return [x0, y0, x1, y1]

def findCongressPerson(name, nicknames_json):
    '''
    Checks the nicknames endpoint of the NYT Congress API
    to determine if the inputted name is that of a member of Congress
    '''
    congress_json = [x['nickname'] for x in nicknames_json if x['nickname'] == name]
    if len(congress_json) > 0:
        print(congress_json)
        return True

    return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)