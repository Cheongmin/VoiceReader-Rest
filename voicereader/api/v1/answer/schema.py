from flask_restplus import fields


def answer_schema(api):
    return api.model("Answer about Question", {
        '_id': fields.String(description='Answer ID', example=''),
        'question_id': fields.String(description='Question ID', example=''),
        'writer_id': fields.String(description='UserID of writer', example=''),
        'contents': fields.String(description='contents of answer', example='<contents>'),
        'created_date': fields.Integer(description='datetiem when create answer', example='')
    })


def post_answer_schema(api):
    return api.model('Post Answer Payload', {
        'display_name': fields.String(description='The Nickname', required=True, example='Lion')
    })
