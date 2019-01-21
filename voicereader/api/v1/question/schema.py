from flask_restplus import fields
from ..user.schema import user_schema


def question_schema(api):
    return api.model('Question', {
        '_id': fields.String(description='Question ID', example='5c3c4fe4182838cf4ea9e6f1'),
        'writer_id': fields.String(description='UserID of writer', example='5c3c4598182838c87f9e1c11'),
        'contents': fields.String(description='contents of question', example='<contents>'),
        'subtitles': fields.String(description='scripts of subtitle', example='<subtitles>'),
        'created_date': fields.Integer(description='datetime when create question', example='1547405521'),
        'sound_url': fields.String(description='sound file url',
                                   example='{base_url}/api/v1/questions/sound/5c3c4fe4182838cf4ea9e6f1.mp3'),
    })


def question_with_writer_schema(api):
    return api.inherit('Question Detail', question_schema(api), {
        'writer': fields.Nested(user_schema(api), description='Infomation of Writer')
    })
