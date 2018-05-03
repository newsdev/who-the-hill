import boto3
import json
import logging
import requests

from image import Image
from abstractrecognizer import AbstractRecognizer

class RekognitionRecognizer(AbstractRecognizer):
    """ An implementation of the AbstractRecognizer class to work with our Rekognition wrapper server """

    def recognize(self, image):
        logging.info("Getting image file")
        image.get_image_file().seek(0)

        client = boto3.client('rekognition')
        r = client.recognize_celebrities(Image={"Bytes": image.get_image_file().read()})

        logging.info("Face object returned: %s" % r)
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
