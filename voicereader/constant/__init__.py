from flask import jsonify

MSG_NOT_EQUAL_IDENTITY = 'not equal between request identity and token identity'
MSG_NOT_FOUND_ELEMENT = "Can't find element"
MSG_INVALID_JSON = "Can't convert json"
MSG_NOT_CONTAIN_SOUND = "Can't find sound file"
MSG_NOT_CONTAIN_FILE = "Can't find file"
MSG_INVALID_FILE = "Can't allowed file"


def msg_json(msg):
    return jsonify({
        "msg": msg
    })


def msg_not_contain_file(name):
    return jsonify({
        "msg": MSG_NOT_CONTAIN_FILE,
        "field_name": name
    })


def msg_invalid_file(name):
    return jsonify({
        "msg": MSG_INVALID_FILE,
        "field_name": name
    })
