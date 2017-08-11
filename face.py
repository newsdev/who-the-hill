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