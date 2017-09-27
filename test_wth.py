import os
import uuid

from face import Face
from image import Image as RecognitionImage
from rekognitionrecognizer import RekognitionRecognizer
from twilio_app import persist_file

media_url="https://pbs.twimg.com/profile_images/681152691461042177/_PrgDgFA.jpg"
target_image = RecognitionImage(image_url=media_url)
recognizer = RekognitionRecognizer(os.environ.get('FACIAL_RECOGNITION_ENDPOINT', None))
recognizer.recognize(target_image)
key_str = 'applications/faces/' + str(uuid.uuid4()) + '.png'
target_image.get_image_file().seek(0)
url = persist_file(key_str, target_image.get_image_file())
print(url)