from flask_restplus import fields


def user_schema(api):
    return api.model('User', {
        '_id': fields.String(description='Id of user', example='5c38b8df18283838d53dfe37'),
        'display_name': fields.String(description='The Nickname', example='Lion'),
        'created_date': fields.Arbitrary(description='user created date', example=1547188815),
        'email': fields.String(description='email of user'),
        'fcm_uid': fields.String(description='unique id from firebase auth'),
    })


def post_user_schema(api):
    return api.model('Post User Payload', {
        'display_name': fields.String(description='The Nickname', required=True, example='Lion')
    })
