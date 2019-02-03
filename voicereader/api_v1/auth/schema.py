from flask_restplus import fields


def access_token_schema(api):
    return api.model('AccessToken Response', {
            'type': fields.String(description='Type of token', example='Bearer'),
            'access_token': fields.String(description='AccessToken', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDczNzk0NjgsIm5iZiI6MTU0NzM3OTQ2OCwianRpIjoiMjMyODU2MTAtNzk2NC00MWI2LWI3ZmMtYWI4NjI3MjY1ZGE0IiwiZXhwIjoxNTQ3NDY1ODY4LCJzdWIiOiI1YzM4YjhkZjE4MjgzODM4ZDUzZGZlMzciLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ._HuELn3mWpd2Y38fV0-drZgq8yx4m-M6mKIWl5eWsgs'),
            'refresh_token': fields.String(description='RefreshToken', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDczNzk0NjgsIm5iZiI6MTU0NzM3OTQ2OCwianRpIjoiNTlmNjdiN2EtOGZhYy00MjQ0LWI4NDMtODVmYzE3YTM4MTBmIiwiZXhwIjoxNTQ5OTcxNDY4LCJzdWIiOiI1YzM4YjhkZjE4MjgzODM4ZDUzZGZlMzciLCJ0eXBlIjoicmVmcmVzaCJ9.a7Th4foyE0NVSzuw3CvaHUZdMcoqA3zjc2PlndeE1fo'),
            'expire_in': fields.Integer(description='Expire time of AccessToken', example=86400)
        })


def refresh_token_schema(api):
    return api.model('AccessToken Response by refresh token', {
            'type': fields.String(description='Type of token', example='Bearer'),
            'access_token': fields.String(description='AccessToken', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDczNzk0NjgsIm5iZiI6MTU0NzM3OTQ2OCwianRpIjoiMjMyODU2MTAtNzk2NC00MWI2LWI3ZmMtYWI4NjI3MjY1ZGE0IiwiZXhwIjoxNTQ3NDY1ODY4LCJzdWIiOiI1YzM4YjhkZjE4MjgzODM4ZDUzZGZlMzciLCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ._HuELn3mWpd2Y38fV0-drZgq8yx4m-M6mKIWl5eWsgs'),
            'expire_in': fields.Integer(description='Expire time of AccessToken', example=86400)
        })
