from flask import Flask
from voicereader.user.controller import get_user_api
from voicereader.question.controller import get_question_api

app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb://localhost:27017/VoiceReader'

app.register_blueprint(get_user_api(app), url_prefix='/api/v1/users')
app.register_blueprint(get_question_api(app), url_prefix='/api/v1/questions')
