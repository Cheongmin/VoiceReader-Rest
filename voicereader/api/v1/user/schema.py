from flask_restplus import fields


def user_schema(api):
    return api.model('User', {
        '_id': fields.String(description='User ID', example='5c38b8df18283838d53dfe37'),
        'display_name': fields.String(description='Nickname', example='Lion'),
        'email': fields.String(description='Email of user', example='lion@example.com'),
        'fcm_uid': fields.String(description='Unique id from firebase auth'),
        'picture': fields.String(description='URL of profile picture'),
        'created_date': fields.Integer(description='user created date', example=1547188815),
    })


def post_user_schema(api):
    return api.model('Post User Payload', {
        'display_name': fields.String(description='The Nickname', required=True, example='Lion')
    })
