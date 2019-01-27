import os


class LocalStorage:
    _upload_path = None

    def init_app(self, app):
        self._upload_path = app.config['RESOURCE_UPLOAD_PATH']

        if not os.path.exists(self._upload_path):
            os.makedirs(self._upload_path)

    def fetch_file(self, resource, filename):
        if self._upload_path is None:
            raise TypeError(self._upload_path)

        return open(os.path.join(self._upload_path, resource, filename), 'rb').read()
        # return send_from_directory(os.path.abspath(self.upload_path), file_name)

    def upload_file(self, resource, file, acl="public-read"):
        if self._upload_path is None:
            raise TypeError(self._upload_path)

        if file is None:
            raise ValueError(file)

        path = os.path.join(self._upload_path, resource, file.filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        file.save(path)
