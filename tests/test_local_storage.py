import os

from flask import Flask

from unittest import TestCase
from werkzeug.datastructures import FileStorage
from voicereader.services.local_storage import LocalStorage
from shutil import rmtree, copy


class LocalStorageTests(TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True

        self.app = app
        self.local_uploader = LocalStorage()

    def tearDown(self):
        upload_path = self.app.config.get('RESOURCE_UPLOAD_PATH')

        if upload_path is not None:
            rmtree(upload_path)

    def test_init_app_ensure_mkdir(self):
        self.app.config['RESOURCE_UPLOAD_PATH'] = 'upload/'

        self.local_uploader.init_app(self.app)

        assert os.path.exists(self.app.config['RESOURCE_UPLOAD_PATH'])

    def test_upload_file_ensure_save(self):
        filename = 'input.txt'
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        with open('tests/testdata/' + filename, 'rb') as fp:
            file = FileStorage(fp, filename=filename)

            self.local_uploader.upload_file(file)

            assert os.path.exists(os.path.join(upload_path, filename))

    def test_upload_file_none_file(self):
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        with self.assertRaises(ValueError):
            self.local_uploader.upload_file(None)

    def test_fetch_file_exists_file(self):
        filename = 'input.txt'
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        os.makedirs(upload_path)
        copy('tests/testdata/' + filename, upload_path)

        binary_file = self.local_uploader.fetch_file(filename)

        with open('tests/testdata/' + filename, 'rb') as src:
            assert src.read() == binary_file

    def test_fetch_file_not_initialized(self):
        filename = 'input.txt'

        with self.assertRaises(TypeError):
            self.local_uploader.fetch_file(filename)

    def test_fetch_file_not_exists_file(self):
        filename = 'NOT_EXISTS_FILE'
        upload_path = 'upload'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        os.makedirs(upload_path)

        with self.assertRaises(FileNotFoundError):
            self.local_uploader.fetch_file(filename)




