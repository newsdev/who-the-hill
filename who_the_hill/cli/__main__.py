import argparse
import glob
import urllib
from io import BytesIO
import json
import os
import uuid
import logging

import boto3
from flask import Flask, request, Response, jsonify, render_template
from google.cloud import storage
from PIL import Image, ImageDraw
import requests
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from rek.models import Alerter
from rek.models import Face
from rek.models import Image as RecognitionImage
from rek.models import RekognitionRecognizer

recognizer = RekognitionRecognizer(os.environ.get('FACIAL_RECOGNITION_ENDPOINT', None))

s3 = boto3.resource(
    's3',
    aws_access_key_id=os.environ.get('AWS_GCS_ACCESS_KEY_ID', None),
    aws_secret_access_key=os.environ.get('AWS_GCS_SECRET_ACCESS_KEY', None),
)
twilio_client = Client(os.environ.get('TWILIO_ACCOUNT_SID', None), os.environ.get('TWILIO_AUTH_TOKEN', None))

recognizer = RekognitionRecognizer(os.environ.get('FACIAL_RECOGNITION_ENDPOINT', None))

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
    """
    Gets a mapping of nicknames to names.
    If there's an api endpoint supplied in the environment variables, it uses that.
    Else the function returns names from a local file.
    """

    # Default case will at least return none.
    nicknames = []
    try:
        with open(local_filename, 'r') as f:
            nicknames = json.loads(f.read())
    except:
        pass

    # nicknames_endpoint = os.environ.get(nickname_env_var, None)
    # if nicknames_endpoint:
    #     try:
    #         response = requests.get(nicknames_endpoint)
    #         nicknames = response.json()
    #     except:
    #         pass
    return nicknames

nicknames = get_nicknames('NICKNAMES_ENDPOINT', 'data/nicknames_dump.json')

def process_faces(image):
    """
    Calls methods to draw boxes around faces and generate response messages for faces.
    """
    logging.debug([x.name for x in image.recognized_faces])
    filtered_objs = [x for x in image.recognized_faces if findCongressPerson(x.name, nicknames)]

    # We're adding back in doppelgangers after filtering so that in case the name of the
    # member of Congress in the doppelgangers file is slightly different from the name in
    # the endpoint/json dump, it'll still be included in the results. Basically, this
    # makes it so that we're not dependent on the exact spellings in the doppelgangers file
    for obj in image.recognized_faces:
        if obj not in filtered_objs and obj.name in doppelgangers:
            obj.name = doppelgangers[obj.name]
            filtered_objs.append(obj)
    colors = draw_bounding_boxes(filtered_objs, image.get_image_file())
    return [generate_message(x, color) for x, color in zip(filtered_objs, colors)]

def generate_message(celeb_obj, color):
    """
    Generates a response message for a celebrity 
    recognition object recieved from Amazon Rekognition.
    """
    name = celeb_obj.name
    confidence = float(celeb_obj.confidence)
    description = "highly unlikely"
    for level in confidence_levels:
        if confidence >= level['prob']:
            description = level['description']
            break

    result = 'We think the %s square is %s, and our confidence level is "%s," or %s.' % (color, name, description, confidence)
    # result  = "{}, {}, {} - confidence = {})".format(name, color, description, confidence)
    return result

def draw_width_rectangle(drawing, coordinates, color, width, fill=None):
    """
    Draws a rectangle of an inputted width using the PIL drawing object
    """
    for i in range(width):
        x0 = coordinates[0] - i
        y0 = coordinates[1] - i
        x1 = coordinates[2] + i
        y1 = coordinates[3] + i
        drawing.rectangle([x0, y0, x1, y1], outline=color)

def draw_bounding_boxes(celeb_objs, file):
    """
    Draws bounding boxes around all faces in inputted file determined by celeb_objs
    """
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
    """
    Calculate face-box coordinates from passed-in ratios and image size.
    """
    x0 = int(bounding_box_ratios['Left'] * float(img_width))
    y0 = int(bounding_box_ratios['Top'] * float(img_height))
    x1 = x0 + int(bounding_box_ratios['Width'] * float(img_width))
    y1 = y0 + int(bounding_box_ratios['Height'] * float(img_height))
    return [x0, y0, x1, y1]

def findCongressPerson(name, nicknames_json):
    """
    Checks the nicknames endpoint of the NYT Congress API
    to determine if the inputted name is that of a member of Congress
    """
    congress_json = [x['nickname'] for x in nicknames_json if x['nickname'] == name]
    if len(congress_json) > 0:
        return True
    return False

def persist_file(filename, uploaded_file):
    """
    Persists a file to google cloud.
    """
    client = storage.Client()
    bucket = client.get_bucket('int.nyt.com')
    blob = bucket.blob(filename)
    blob.upload_from_string(uploaded_file.read(), content_type="image/png")
    return blob.public_url.replace('applications%2Ffaces%2F', 'applications/faces/').replace('storage.googleapis.com/', '')


def get_doppelgangers(doppelganger_filename):
    with open(doppelganger_filename, 'r') as f:
        return json.loads(f.read())

doppelgangers = get_doppelgangers('data/doppelgangers.json')

def getRecipients():
    """
    Fetch email recipients from environment variable.
    """
    emails = os.environ.get("EMAIL_RECIPIENTS", "jeremy.bowers@nytimes.com")
    emails = emails.split(" ")
    return emails

def recognize(images):
    """
    Fetches image from incoming text message. Sends image to app.py (Amazon Rekognition) for analysis.
    Sends reply text message.
    """

    report = []

    print("*****************************")
    print("******* WHO THE HILL *******")
    print("****************************")
    print("Preparing to analyze %s images." % len(images))
    print("")

    for i in images:
        print("Analyzing: %s" % i)
        with open(i, 'rb') as readfile:
            timestamp = str(uuid.uuid4())
            key_str = 'applications/faces/' + timestamp + '.png'
            image_url = persist_file(key_str, readfile)
        target_image = RecognitionImage(image_url=image_url)
        recognizer.recognize(target_image)
        print("Found: %s faces" % len(target_image.recognized_faces))

        if len(target_image.recognized_faces) > 0:
            face_messages = process_faces(target_image)
            for message in face_messages:
                print("* %s" % message)
            timestamp = str(uuid.uuid4())
            key_str = 'applications/faces/' + timestamp + '.png'
            target_image.get_image_file().seek(0)
            url = persist_file(key_str, target_image.get_image_file())
            print(url)

            report.append({"faces": face_messages, "url": url})
            print("")

    if len(report) > 0:
        with open('report.json', 'w') as writefile:
            writefile.write(json.dumps(report))

if __name__ == "__main__":
    data_dir = None
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", "-d", help="directory of images to analyze",
                        action="store")
    args = parser.parse_args()
    data_dir = args.directory
    if not data_dir:
        data_dir = os.environ.get('DATA_DIR', None)

    if data_dir:
        images = []
        images += glob.glob('%s*.png' % data_dir)
        images += glob.glob('%s*.jpg' % data_dir)
        recognize(images)

    else:
        print("Traceback (most recent call last):")
        print(" Missing `data_dir` variable")
        print(" Must specify a data directory with either --directory or export DATA_DIR")