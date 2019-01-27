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

        if upload_path is not None and os.path.exists(upload_path):
            rmtree(upload_path)

    def test_upload_file_ensure_save(self):
        resource = 'test-resource'
        filename = 'input.txt'
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        with open('tests/testdata/' + filename, 'rb') as fp:
            file = FileStorage(fp, filename=filename)

            self.local_uploader.upload_file(resource, file)

            assert os.path.exists(os.path.join(upload_path, resource, filename))

    def test_upload_file_none_file(self):
        resource = 'test-resource'
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        with self.assertRaises(ValueError):
            self.local_uploader.upload_file(resource, None)

    def test_fetch_file_exists_file(self):
        resource = 'test-resource'
        filename = 'input.txt'
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        os.makedirs(os.path.join(upload_path, resource))
        copy('tests/testdata/' + filename, os.path.join(upload_path, resource))

        binary_file = self.local_uploader.fetch_file(resource, filename)

        with open('tests/testdata/' + filename, 'rb') as src:
            assert src.read() == binary_file

    def test_fetch_file_not_initialized(self):
        resource = 'test-resource'
        filename = 'input.txt'

        with self.assertRaises(TypeError):
            self.local_uploader.fetch_file(resource, filename)

    def test_fetch_file_not_exists_file(self):
        resource = 'test-resource'
        filename = 'NOT_EXISTS_FILE'
        upload_path = 'upload'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        with self.assertRaises(FileNotFoundError):
            self.local_uploader.fetch_file(resource, filename)




