import datetime

from flask import jsonify, current_app
from flask_restplus import Namespace, Resource
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity

from werkzeug.exceptions import NotFound, Unauthorized
from firebase_admin import auth, initialize_app, credentials

from .schema import access_token_schema, refresh_token_schema
from ..user.resource import get_user_id

credential = credentials.Certificate('firebase-adminsdk.json')
firebase_app = initialize_app(credential)

api = Namespace('Oauth2 API', description='Oauth2 related operation')

get_parser = api.parser()
get_parser.add_argument('Authorization', location='headers', required=True, help='IdToken from firebase auth')

post_parser = api.parser()
post_parser.add_argument('Authorization', location='headers', required=True, help='Bearer <refresh_token>')


def _access_token_expire_delta():
    return datetime.timedelta(seconds=_access_token_expire_in())


def _access_token_expire_in():
    return current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SEC']


def _refresh_token_expire_delta():
    return datetime.timedelta(seconds=_refresh_token_expire_in())


def _refresh_token_expire_in():
    return current_app.config['JWT_REFRESH_TOKEN_EXPIRES_SEC']


@api.route('/token')
class Token(Resource):
    @api.doc(description='Generate new AccessToken by firebase auth idToken')
    @api.expect(get_parser)
    @api.response(200, 'Success', access_token_schema(api))
    @api.response(400, 'Failed when not include "Authorization" header')
    @api.response(401, 'Failed when request id token is invalid')
    @api.response(404, 'Failed  when not registered id token')
    def get(self):
        args = get_parser.parse_args()

        id_token = args['Authorization']

        try:
            decoded_token = auth.verify_id_token(id_token, firebase_app)
        except ValueError as ex:
            raise Unauthorized(str(ex))

        firebase_uid = decoded_token['sub']

        user_id = get_user_id(firebase_uid)
        if not user_id:
            raise NotFound('Not registered id token')

        access_token = create_access_token(user_id, expires_delta=_access_token_expire_delta())
        refresh_token = create_refresh_token(user_id, expires_delta=_refresh_token_expire_delta())
        expire_in = _access_token_expire_in()

        return jsonify({
            "type": "Bearer",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expire_in": expire_in
        })

    @jwt_refresh_token_required
    @api.doc(description='fetch new AccessToken by RefreshToken')
    @api.expect(post_parser)
    @api.response(200, 'Success', refresh_token_schema(api))
    @api.response(400, 'Failed when not include "Authorization" header')
    @api.response(401, 'Failed when invalid refresh_token')
    def post(self):
        user_id = get_jwt_identity()

        access_token = create_access_token(user_id, expires_delta=_access_token_expire_delta())
        expire_in = _access_token_expire_in()

        return jsonify({
            "type": "Bearer",
            "access_token": access_token,
            "expire_in": expire_in
        })


