import requests
from io import BytesIO

from face import Face

class Image:
    """
    A class to store an image and its facial recognition information
    in a non-json-dependent form
    """

    def __init__(self, image_url='', image_file=None):
        self.image_url = image_url
        self.image_file = image_file
        self.recognized_faces = []
        self.boxed_image = None
        

    def to_dict(self):
        """
        Returns a jsonifyable dict of this image
        """
        results = []
        for face in recognized_faces:
            results.append(face.to_dict())
        
        return results

    def add_face(self, left, top, width, height, confidence, name):
        """ Add a new face to the list of recognized faces in this image

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
        """ Returns a file object containing the image this object contains, fetching it from a url if necessary
        """
        if self.image_file is None and self.image_url != '':
            self.image_file = self._get_image_from_url(self.image_url)
        
        return self.image_file

    def _get_image_from_url(self, image_url):
        ''' Get image file object from passed-in url. '''
        req = requests.get(image_url, headers={'User-Agent' : "Magic Browser"})
        image_page = req.content
        f = BytesIO(image_page)
        return f

    def __del__(self):
        '''Close the file object if one exists for this image'''
        if self.image_file is not None:
            self.image_file.close()