from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO
import json
import time
import os

import boto3
from botocore.exceptions import ClientError
import requests


class Alerter:
    """ Alerts program manager of potential abuse of a program. 

        Args:
            counter_limit (int): The max amount of program uses per time interval.
            time_interval (int): Time alloted per interval, measured in seconds.
            recipients (list): Emails to which Alerter will send potential abuse warnings.
    """
    def __init__(self, counter_limit, time_interval, recipients):
        self.counter = 0
        self.time_interval_start = time.time()
        self.counter_limit = counter_limit
        self.time_interval = time_interval
        self.recipients = recipients
        self.client = boto3.client('ses',region_name=os.environ.get("AWS_DEFAULT_REGION", None), aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID_EMAIL", None), aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY_EMAIL", None))

    def increment_counter(self):
        """ Increment counter by 1. """
        self.counter += 1

    def check_for_counter_limit(self):
        """ Check if counter if greater than or equal to the counter limit. """
        return self.counter >= self.counter_limit

    def reset_counter(self):
        """ Set counter to 0. """
        self.counter = 0

    def check_for_time_interval(self):
        """ Check if the passed-in time interval has passed. """
        return (time.time() - self.time_interval_start) >= self.time_interval

    def reset_time_interval(self):
        """ Reset time interval. """
        self.time_interval_start = time.time()

    def abuse_check(self):
        """ 
        Check if the counter limit has been passed within the given time interval. If so, notify 
        program manager of potential abuse.
        """
        self.increment_counter()

        if (self.check_for_counter_limit() and (not self.check_for_time_interval())):
            for recipient in self.recipients:
                self.send_email(recipient)
            self.reset_counter()
            self.reset_time_interval()
        elif (self.check_for_time_interval()):
            self.reset_counter()
            self.reset_time_interval()


    def send_email(self, recipient):
        # The sender of the email.
        sender = os.environ.get("EMAIL_SENDER", None)

        # The character encoding for the email.
        charset = "UTF-8"

        # The subject line for the email.
        subject = "Who The Hill - Alert!"

        # The current time
        hour = datetime.now().time().hour
        minute = datetime.now().time().minute
        time_of_day = "a.m."
        if hour > 11: 
            hour = (hour % 12) + 1
            time_of_day = "p.m."
        if minute < 10: 
            minute = "0" + str(minute)
        current_time = "{0}:{1} {2}".format(hour, minute, time_of_day)

        # The HTML body of the email.
        htmlbody = """<p>At {0}, more than {1} text messages were sent to Who The Hill. This occurred before a full time interval of {2} seconds passed. Only {3} seconds have passed. Please be aware of potential abuse of the application. Nobody likes high Twilio costs!</p>""".format(current_time, self.counter_limit, self.time_interval, (time.time() - self.time_interval_start))

        # The email body for recipients with non-HTML email clients.  
        textbody = "At {0}, more than {1} text messages were sent to Who The Hill. This occurred before a full time interval of {2} seconds passed. Only {3} seconds have passed. Please be aware of potential abuse of the application. Nobody likes high Twilio costs!".format(current_time, self.counter_limit, self.time_interval, (time.time() - self.time_interval_start))

        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': htmlbody,
                        },
                        'Text': {
                            'Charset': charset,
                            'Data': textbody,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': subject,
                    },
                },
                Source=sender,
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['ResponseMetadata']['RequestId'])


class Face:
    """ Stores recognition data for a face.

        Args:
            left (float): the left side of the face's bounding box as a fraction of the image width
            top (float): the top side of the face's bounding box as a fraction of the image height
            width (float): the width of the face's bounding box as a fraction of the overall image width
            height (float): the height of the face's bounding box as a fraction of the overall image height
            confidence (float): the confidence of the face's recognition, from 0 to 100
            name (string): the name of the face recognized
    """

    def __init__(self, left=-1, top=-1, width=-1, height=-1, confidence=-1, name=''):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.confidence = confidence
        self.name = name

    def to_dict(self):
        """
        Returns a jsonifyable dict of this image
        """
        face_object = {}
        bounding_box = {}
        bounding_box['Left'] = self.left
        bounding_box['Top'] = self.top
        bounding_box['Height'] = self.height
        bounding_box['Width'] = self.width
        face_object['BoundingBox'] = bounding_box
        face_object['MatchConfidence'] = self.confidence
        face_object['Name'] = self.name
        return face_object


class Image:
    """
    A class to store an image and its facial recognition information
    in a non-json-dependent form.
    """

    def __init__(self, image_url='', image_file=None):
        self.image_url = image_url
        self.image_file = image_file
        self.recognized_faces = []
        self.boxed_image = None
        

    def to_dict(self):
        """
        Returns a jsonifyable dict of this image.
        """
        results = []
        for face in recognized_faces:
            results.append(face.to_dict())
        
        return results

    def add_face(self, left, top, width, height, confidence, name):
        """ 
        Add a new face to the list of recognized faces in this image

        Args:
            left (float): the left side of the face's bounding box as a fraction of the image width
            top (float): the top side of the face's bounding box as a fraction of the image height
            width (float): the width of the face's bounding box as a fraction of the overall image width
            height (float): the height of the face's bounding box as a fraction of the overall image height
            confidence (float): the confidence of the face's recognition, from 0 to 100
            name (string): the name of the face recognized
        """
        new_face = Face(left, top, width, height, confidence, name)
        self.recognized_faces.append(new_face)

    
    def get_image_file(self):
        """ 
        Returns a file object containing the image this object 
        contains, fetching it from a url if necessary.
        """
        if self.image_file is None and self.image_url != '':
            self.image_file = self._get_image_from_url(self.image_url)
        
        return self.image_file

    def _get_image_from_url(self, image_url):
        """
        Get image file object from passed-in url.
        """
        req = requests.get(image_url, headers={'User-Agent' : "Magic Browser"})
        image_page = req.content
        f = BytesIO(image_page)
        return f

    def __del__(self):
        """
        Close the file object if one exists for this image.
        """
        if self.image_file is not None:
            self.image_file.close()


class AbstractRecognizer:
    """ A base class for facial recognition service interfaces

        Args:
            recognition_endpoint (string): The url of the recognition service (theoretically could be something other than a string...maybe an object)
    """

    def __init__(self, recognition_endpoint):
        self.recognition_endpoint = recognition_endpoint

    @abstractmethod
    def recognize(self, image):
        """ Implement this method to interface with the recognition service and add results to an image object

            Args:
                image (RecognitionImage): An object containing an image file to be sent to the recognizer and which will be populated with the recognition information
        """
        pass


class RekognitionRecognizer(AbstractRecognizer):
    """ An implementation of the AbstractRecognizer class to work with our Rekognition wrapper server """

    def recognize(self, image):
        print("Getting image file")
        image.get_image_file().seek(0)

        client = boto3.client('rekognition')
        r = client.recognize_celebrities(Image={"Bytes": image.get_image_file().read()})

        print("Face object returned: %s" % r)
        face_obj = (r)

        if ("CelebrityFaces" in face_obj and len(face_obj['CelebrityFaces']) > 0):
            celeb_objs = face_obj['CelebrityFaces']
            for obj in celeb_objs:
                bounding_box = obj['Face']['BoundingBox']
                image.add_face(
                    bounding_box['Left'],
                    bounding_box['Top'],
                    bounding_box['Width'],
                    bounding_box['Height'],
                    obj['MatchConfidence'],
                    obj['Name']
                )
        return image
