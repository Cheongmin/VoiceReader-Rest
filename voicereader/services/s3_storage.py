import os
import boto3

from botocore.exceptions import ClientError


class S3Storage:
    _bucket_name = None
    _s3 = None

    def init_app(self, app):
        self._bucket_name = app.config['S3_BUCKET_NAME']
        self._s3 = boto3.client(
            "s3",
            region_name=app.config['S3_REGION'],
            aws_access_key_id=app.config['S3_KEY'],
            aws_secret_access_key=app.config['S3_SECRET']
        )

    def fetch_file(self, resource, filename):
        if self._s3 is None:
            raise TypeError(self._s3)

        if self._bucket_name is None:
            raise TypeError(self._bucket_name)

        if resource is None:
            raise ValueError(resource)

        if filename is None:
            raise ValueError

        key = os.path.join(resource, filename)

        try:
            file = self._s3.get_object(Bucket=self._bucket_name, Key=key)
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'NoSuchKey':
                return None
            else:
                raise ex

        return file['Body'].read()

    def upload_file(self, resource, file):
        if self._s3 is None:
            raise TypeError(self._s3)

        if self._bucket_name is None:
            raise TypeError(self._bucket_name)

        if resource is None:
            raise ValueError(resource)

        if file is None:
            raise ValueError(file)

        key = os.path.join(resource, file.filename)

        self._s3.upload_fileobj(file, self._bucket_name, Key=key, ExtraArgs={
            "ContentType": file.content_type,
        })
