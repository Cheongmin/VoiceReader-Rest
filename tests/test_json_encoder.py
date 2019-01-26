from bson import ObjectId
from voicereader.extensions.json_encoder import JSONEncoder


def test_object_id_encode():
    expected = '5c38b8df18283838d53dfe37'
    object_id = ObjectId(expected)

    actual = JSONEncoder().default(object_id)

    assert expected == actual


