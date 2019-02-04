import boto3
import pytest
import io

from botocore.exceptions import ClientError

from werkzeug.datastructures import FileStorage
from voicereader.services.s3_storage import S3Storage


@pytest.fixture(scope='session')
def mock_boto_client():
    class MockBotoClient:
        def get_object(self, *args, **kwargs):
            return {
                'Body': io.BytesIO(b'Hello World')
            }

        def upload_fileobj(self, *args, **kwargs):
            pass

    return MockBotoClient()


@pytest.fixture(scope='function')
def storage(monkeypatch, mock_boto_client):
    storage = S3Storage()

    monkeypatch.setattr(storage, '_bucket_name', 'EXISTS_BUCKET_NAME')
    monkeypatch.setattr(storage, '_s3', mock_boto_client)

    return storage


def test_init_app(monkeypatch, storage, flask_app):
    monkeypatch.setattr(storage, '_s3', None)
    monkeypatch.setattr(boto3, 'client', lambda *args, **kwargs: '')

    flask_app.config['S3_BUCKET_NAME'] = 'TEST-BUCKET'
    flask_app.config['S3_REGION'] = 'TEST_REGION'
    flask_app.config['S3_KEY'] = 'TEST_KEY'
    flask_app.config['S3_SECRET'] = 'TEST SECRET'

    storage.init_app(flask_app)

    assert storage._bucket_name == 'TEST-BUCKET'
    assert storage._s3 is not None


def test_fetch_file(storage, mock_boto_client):
    binary = storage.fetch_file('EXISTS_RESOURCE', 'FILE_NAME')

    assert isinstance(binary, bytes)


def test_fetch_file_none_s3(monkeypatch, storage):
    monkeypatch.setattr(storage, '_s3', None)

    with pytest.raises(TypeError):
        storage.fetch_file('VALID_FILE_RESOURCE', 'VALID_FILE_NAME')


def test_fetch_file_none_bucket_name(monkeypatch, storage):
    monkeypatch.setattr(storage, '_bucket_name', None)

    with pytest.raises(TypeError):
        storage.fetch_file('VALID_FILE_RESOURCE', 'VALID_FILE_NAME')


def test_fetch_file_none_resource(storage):
    with pytest.raises(ValueError):
        storage.fetch_file(None, 'VALID_FILE_NAME')


def test_fetch_file_none_filename(storage):
    with pytest.raises(ValueError):
        storage.fetch_file('VALID_FILE_RESOURCE', None)


def test_fetch_file_not_exists_file(monkeypatch, storage):
    def mock_get_object(Bucket, Key):
        raise ClientError({
            'Error': {
                'Code': 'NoSuchKey'
            }
        }, None)

    monkeypatch.setattr(storage._s3, 'get_object', mock_get_object)

    expected = None

    actual = storage.fetch_file('VALID_FILE_RESOURCE', 'NOT_EXISTS_FILE')

    assert expected == actual


def test_upload_file(storage):
    with open('tests/testdata/input.txt') as fp:
        storage.upload_file('EXISTS_RESOURCE', FileStorage(fp))


def test_upload_file_none_s3(monkeypatch, storage):
    monkeypatch.setattr(storage, '_s3', None)

    with open('tests/testdata/input.txt') as fp:
        with pytest.raises(TypeError):
            storage.upload_file('VALID_FILE_RESOURCE', FileStorage(fp))


def test_upload_file_none_bucket_name(monkeypatch, storage):
    monkeypatch.setattr(storage, '_bucket_name', None)

    with open('tests/testdata/input.txt') as fp:
        with pytest.raises(TypeError):
            storage.upload_file('VALID_FILE_RESOURCE', FileStorage(fp))


def test_upload_file_none_resource(storage):
    with open('tests/testdata/input.txt') as fp:
        with pytest.raises(ValueError):
            storage.upload_file(None, FileStorage(fp))


def test_upload_file_none_file(storage):
    with pytest.raises(ValueError):
        storage.upload_file('EXISTS_RESOURCE', None)
