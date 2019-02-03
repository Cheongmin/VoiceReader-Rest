from unittest import TestCase
from bson import ObjectId
from voicereader.extensions.json_encoder import JSONEncoder


class JSONEncoderTests(TestCase):
    def setUp(self):
        self.json_encoder = JSONEncoder()

    def test_object_id_encode(self):
        expected = '5c38b8df18283838d53dfe37'
        object_id = ObjectId(expected)

        actual = self.json_encoder.default(object_id)

        assert expected == actual

    def test_undefined_model_encode(self):
        class Undefined:
            pass

        undefined = Undefined()

        with self.assertRaises(TypeError):
            self.json_encoder.default(undefined)
