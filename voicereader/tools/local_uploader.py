import os
from flask import send_from_directory


class LocalUploader:
    def __init__(self, upload_path):
        self.upload_path = upload_path

    def init_app(self, app):
        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)

    def fetch_file(self, file_name):
        return send_from_directory(os.path.abspath(self.upload_path), file_name)

    def upload_file(self, file, acl="public-read"):
        file.save(os.path.join(self.upload_path, file.filename))
