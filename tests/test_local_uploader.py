import os

from flask import Flask

from unittest import TestCase
from werkzeug.datastructures import FileStorage
from voicereader.services.local_uploader import LocalUploader
from shutil import rmtree


class LocalUploaderTests(TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['TESTING'] = True

        self.app = app
        self.local_uploader = LocalUploader()

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

        with open('tests/testdata/' + filename) as fp:
            file = FileStorage(fp, filename=filename)

            self.local_uploader.upload_file(file)

            assert os.path.exists(os.path.join(upload_path, filename))

    def test_upload_file_none_file(self):
        upload_path = 'upload/'

        self.local_uploader.upload_path = self.app.config['RESOURCE_UPLOAD_PATH'] = upload_path

        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        self.assertRaises(TypeError, self.local_uploader.upload_file(None))



