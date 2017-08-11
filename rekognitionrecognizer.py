import json
import requests

from image import Image
from abstractrecognizer import AbstractRecognizer

class RekognitionRecognizer(AbstractRecognizer):
    """ An implementation of the AbstractRecognizer class to work with our Rekognition wrapper server """

    def recognize(self, image):
        image.get_image_file().seek(0)
        r = requests.post(self.recognition_endpoint, files={'file': image.get_image_file().read()})
        face_obj = json.loads(r.text)
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
