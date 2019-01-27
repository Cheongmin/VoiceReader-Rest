import boto3
from flask import make_response


class S3Storage:
    s3 = None
    bucket_name = None

    def init_app(self, app):
        self.bucket_name = app.config['S3_BUCKET_NAME']

        self.s3 = boto3.client(
            "s3",
            region_name=app.config['S3_REGION'],
            aws_access_key_id=app.config['S3_KEY'],
            aws_secret_access_key=app.config['S3_SECRET']
        )

    def fetch_file(self, prefix, file_name, as_attachment=False):
        key = '{}{}'.format(prefix, file_name)

        file = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        response = make_response(file['Body'].read())
        response.headers['Content-Type'] = file['ContentType']

        if as_attachment:
            response.headers['Content-Disposition'] = 'attachment'

        return response

    def upload_file(self, prefix, file):
        key = '{}{}'.format(prefix, file.filename)

        self.s3.upload_fileobj(file, self.bucket_name, Key=key, ExtraArgs={
            "ContentType": file.content_type,
        })
