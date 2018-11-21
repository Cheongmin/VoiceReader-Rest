from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from firebase_admin import auth, initialize_app, credentials
from voicereader.constant import action_result
from voicereader.constant import msg_json, MSG_NOT_FOUND_ELEMENT
from binascii import Error

import requests

_auth_api = Blueprint('auth', __name__)

credential = credentials.Certificate('firebase-adminsdk.json')
firebase_app = initialize_app(credential)


def get_auth_api():
    return _auth_api


@_auth_api.route('token', methods=['GET'])
def get_access_token():
    id_token = request.headers['Authorization']

    try:
        decode_token = auth.verify_id_token(id_token, firebase_app)
        fcm_uid = decode_token['sub']

        url = request.host_url + 'api/v1/users'
        querystring = {"fcm_uid": fcm_uid}

        response = requests.request("GET", url, params=querystring)
        if response.status_code == 404:
            return action_result.not_found(msg_json(MSG_NOT_FOUND_ELEMENT))
        elif response.status_code != 200:
            return action_result.internal_server_error(response.text)

        access_token = create_access_token(identity=response.text)
        refresh_token = create_refresh_token(identity=response.text)

        return action_result.ok(jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        }))
    except Error as ex:
        return action_result.unauthorized(msg_json(str(ex)))
    except ValueError as ex:
        return action_result.unauthorized(msg_json(str(ex)))
    except Exception as ex:
        return action_result.unauthorized(msg_json(str(ex)))
