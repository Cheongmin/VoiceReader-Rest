import os


class LocalStorage:
    _upload_path = None

    def init_app(self, app):
        self._upload_path = app.config['RESOURCE_UPLOAD_PATH']

    def fetch_file(self, resource, filename):
        if self._upload_path is None:
            raise TypeError(self._upload_path)

        if resource is None:
            raise ValueError(resource)

        if filename is None:
            raise ValueError(resource)

        return open(os.path.join(self._upload_path, resource, filename), 'rb').read()

    def upload_file(self, resource, file):
        if self._upload_path is None:
            raise TypeError(self._upload_path)

        if resource is None:
            raise ValueError(file)

        if file is None:
            raise ValueError(file)

        path = os.path.join(self._upload_path, resource, file.filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        file.save(path)
