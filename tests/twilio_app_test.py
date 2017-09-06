import unittest
import twilio_app

class MyObject():
    name = "Jimmy"
    confidence = 84

class TwilioAppTest(unittest.TestCase):
    def setUp(self):

        self.twilio_app = twilio_app
        self.celeb_obj = MyObject()
        self.color = "blue"

    def test_generate_message(self):
        result = self.twilio_app.generate_message(self.celeb_obj, self.color)
        self.assertEqual(result, "Jimmy (blue, good chance - confidence = 84.0)")

    def test_findCongressPerson_false(self):
        result = self.twilio_app.findCongressPerson("Will Smith", self.twilio_app.nicknames)
        self.assertEqual(result, False)

    def test_findCongressPerson_true(self):
        result = self.twilio_app.findCongressPerson("Joe Kennedy", self.twilio_app.nicknames)
        self.assertEqual(result, True)

if __name__ == '__main__':
    unittest.main()