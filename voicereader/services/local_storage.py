import os


class LocalStorage:
    upload_path = None

    def init_app(self, app):
        self.upload_path = app.config['RESOURCE_UPLOAD_PATH']

        if not os.path.exists(self.upload_path):
            os.makedirs(self.upload_path)

    def fetch_file(self, file_name):
        if self.upload_path is None:
            raise TypeError(self.upload_path)

        return open(os.path.join(self.upload_path, file_name), 'rb').read()
        # return send_from_directory(os.path.abspath(self.upload_path), file_name)

    def upload_file(self, file, acl="public-read"):
        if self.upload_path is None:
            raise TypeError(self.upload_path)

        if file is None:
            raise ValueError(file)

        file.save(os.path.join(self.upload_path, file.filename))
