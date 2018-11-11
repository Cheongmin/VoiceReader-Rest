from flask import Flask
from voicereader.user.controller import user_api
from voicereader.question.controller import question_api

app = Flask(__name__)

app.register_blueprint(user_api, url_prefix='/api/v1/users')
app.register_blueprint(question_api, url_prefix='/api/v1/questions')
