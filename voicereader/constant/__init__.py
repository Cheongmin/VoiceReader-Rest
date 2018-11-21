from flask import jsonify

MSG_NOT_EQUAL_IDENTITY = 'not equal between request identity and token identity'
MSG_NOT_FOUND_ELEMENT = "Can't find element"
MSG_INVALID_JSON = "Can't convert json"
MSG_NOT_CONTAIN_SOUND = "Can't find sound file"


def msg_json(msg):
    return jsonify({
        "msg": msg
    })
