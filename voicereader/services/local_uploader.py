import os
from flask import send_from_directory


class LocalUploader:
    upload_path = ''

    def init_app(self, app):
        self.upload_path = app.config['RESOURCE_UPLOAD_PATH']

        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)

    def fetch_file(self, file_name):
        return send_from_directory(os.path.abspath(self.upload_path), file_name)

    def upload_file(self, file, acl="public-read"):
        file.save(os.path.join(self.upload_path, file.filename))
