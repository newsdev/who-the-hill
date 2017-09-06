import unittest
from face import Face

class FaceTest(unittest.TestCase):
    def setUp(self):
        dummy_data = {"left": 100, "top": 110, "width": 120, "height": 130, "confidence": 99, "name": "Dummy"}

        self.my_face_dummy = Face(dummy_data["left"], dummy_data["top"], dummy_data["width"], dummy_data["height"], dummy_data["confidence"], dummy_data["name"])

        self.my_face = Face()

    def test_my_face_dummy_confidence(self):
        self.assertTrue(self.my_face_dummy.to_dict()["MatchConfidence"] > -1)

    def test_my_face_dummy_bounding_box(self):
        for k,v in self.my_face_dummy.to_dict()["BoundingBox"].items():
            with self.subTest(k=k, v=v):
                self.assertTrue(v > -1)


if __name__ == '__main__':
    unittest.main()