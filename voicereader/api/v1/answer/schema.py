from flask_restplus import fields


def answer_schema(api):
    return api.model("Answer about Question", {
        '_id': fields.String(description='Answer ID', example='5c3c53a4182838d29bf3e947'),
        'question_id': fields.String(description='Question ID', example='5c3c5342182838d04963fb6a'),
        'writer_id': fields.String(description='UserID of writer', example='5c3c53a4182838d29bf3e948'),
        'contents': fields.String(description='contents of answer', example='<contents>'),
        'created_date': fields.Integer(description='datetiem when create answer', example='1547425044')
    })


def post_answer_schema(api):
    return api.model('Post Answer Payload', {
        'contents': fields.String(description='contents of answer', example='<contents>', required=True)
    })
