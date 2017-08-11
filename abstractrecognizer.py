from abc import ABC, abstractmethod

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