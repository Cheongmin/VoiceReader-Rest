from flask_restplus import fields


def question_schema(api):
    return api.model('Question', {
        '_id': fields.String(description='Question ID', example=''),
        'writer_id': fields.String(description='UserID of writer', example=''),
        'contents': fields.String(description='contents of question', example='<contents>'),
        'subtitles': fields.String(description='scripts of subtitle', example='<subtitles>'),
        'created_date': fields.Integer(description='datetime when create question', example=''),
        'sound_url': fields.Url(description='sound file url', example=''),
    })
