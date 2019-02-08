# Defines a user that should be able to access to s3 bucket
resource "aws_iam_user" "boto3" {
    name = "${var.iam_boto_s3}"
}

resource "aws_iam_access_key" "boto3" {
    user = "${aws_iam_user.boto3.name}"
}

resource "aws_iam_user_policy" "boto3" {
    name = "boto3_policy"
    user = "${aws_iam_user.boto3.name}"
    policy= <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::${var.s3_resource_name}",
                "arn:aws:s3:::${var.s3_resource_name}/*"
            ]
        }
   ]
}
EOF
}

resource "aws_s3_bucket" "s3_resource" {
  bucket = "${var.s3_resource_name}"
  acl = "private"

  policy = <<EOF
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "AWS": "${aws_iam_user.boto3.arn}"
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::${var.s3_resource_name}",
                "arn:aws:s3:::${var.s3_resource_name}/*"
            ]
        }
    ]
}
EOF
}

resource "aws_s3_bucket_object" "default_user_profile_image" {
  key        = "user-picture/default_user_profile.png"
  bucket     = "${aws_s3_bucket.s3_resource.id}"
  source     = "${var.default_profile_path}"
}

resource "aws_s3_bucket_public_access_block" "s3_resource_access_block" {
  bucket = "${aws_s3_bucket.s3_resource.id}"

  # Block new public ACLs and uploading public objects
  block_public_acls = true

  # Retroactively remove public access granted through public ACLs
  ignore_public_acls = true

  # Block new public bucket policies
  block_public_policy = true

  # Retroactivley block public and cross-account access if bucket has public policies
  restrict_public_buckets = true
}