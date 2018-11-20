from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from firebase_admin import auth, initialize_app, credentials
from binascii import Error

import requests

_auth_api = Blueprint('auth', __name__)

credential = credentials.Certificate('voicereader-fe99d-firebase-adminsdk-b4d03-ad5f75cefc.json')
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
            return '', 404
        elif response.status_code != 200:
            return '', 500

        access_token = create_access_token(identity=response.text)
        refresh_token = create_refresh_token(identity=response.text)

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        })
    except Error as ex:
        return str(ex), 401
    except ValueError as ex:
        return str(ex), 401
