import os

from flask import Flask

from unittest import TestCase
from werkzeug.datastructures import FileStorage
from voicereader.services.local_storage import LocalStorage
from shutil import rmtree, copy


class LocalStorageTests(TestCase):
    def setUp(self):
        self.storage = LocalStorage()

    def tearDown(self):
        upload_path = self.storage._upload_path

        if upload_path is not None and os.path.exists(upload_path):
            rmtree(upload_path)

    def test_init_app(self):
        expected_upload_path = 'upload/'

        flask_app = Flask(__name__)
        flask_app.config['TESTING'] = True
        flask_app.config['RESOURCE_UPLOAD_PATH'] = expected_upload_path

        self.storage.init_app(flask_app)

        assert expected_upload_path == self.storage._upload_path

    def test_upload_file_ensure_save(self):
        resource = 'test-resource'
        filename = 'input.txt'
        upload_path = 'upload/'

        self.storage._upload_path = upload_path

        with open('tests/testdata/' + filename, 'rb') as fp:
            file = FileStorage(fp, filename=filename)

            self.storage.upload_file(resource, file)

            assert os.path.exists(os.path.join(upload_path, resource, filename))

    def test_upload_file_not_initialized(self):
        with open('tests/testdata/input.txt', 'rb') as fp:
            file = FileStorage(fp)

            with self.assertRaises(TypeError):
                self.storage.upload_file("EXISTS_RESOURCE", file)

    def test_upload_file_none_resource(self):
        filename = 'input.txt'
        upload_path = 'upload/'

        self.storage._upload_path = upload_path

        with open('tests/testdata/' + filename, 'rb') as fp:
            file = FileStorage(fp, filename=filename)

            with self.assertRaises(ValueError):
                self.storage.upload_file(None, file)

    def test_upload_file_none_file(self):
        resource = 'test-resource'
        upload_path = 'upload/'

        self.storage._upload_path = upload_path

        with self.assertRaises(ValueError):
            self.storage.upload_file(resource, None)

    def test_fetch_file_exists_file(self):
        resource = 'test-resource'
        filename = 'input.txt'
        upload_path = 'upload/'

        self.storage._upload_path = upload_path

        os.makedirs(os.path.join(upload_path, resource))
        copy('tests/testdata/' + filename, os.path.join(upload_path, resource))

        binary_file = self.storage.fetch_file(resource, filename)

        with open('tests/testdata/' + filename, 'rb') as src:
            assert src.read() == binary_file

    def test_fetch_file_not_exists_file(self):
        resource = 'test-resource'
        filename = 'NOT_EXISTS_FILE'
        upload_path = 'upload/'

        self.storage._upload_path = upload_path

        with self.assertRaises(FileNotFoundError):
            self.storage.fetch_file(resource, filename)

    def test_fetch_file_not_initialized(self):
        resource = 'test-resource'
        filename = 'input.txt'

        with self.assertRaises(TypeError):
            self.storage.fetch_file(resource, filename)

    def test_fetch_file_none_resource(self):
        self.storage._upload_path = 'upload/'

        with self.assertRaises(ValueError):
            self.storage.fetch_file(None, 'EXISTS_FILE_NAME')

    def test_fetch_file_none_filename(self):
        self.storage._upload_path = 'upload/'

        with self.assertRaises(ValueError):
            self.storage.fetch_file('EXISTS_RESOURCE', None)




