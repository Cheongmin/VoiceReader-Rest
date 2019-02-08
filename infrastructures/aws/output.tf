output "S3_BUCKET_NAME" {
  description = "S3 Name required config.production.json"
  value       = "${aws_s3_bucket.s3_resource.id}"
}

output "S3_REGION" {
  description = "S3 Region required config.production.json"
  value       = "${aws_s3_bucket.s3_resource.region}"
}

output "S3_KEY" {
  description = "S3 Key required config.production.json"
  value       = "${aws_iam_access_key.boto3.id}"
}

output "S3_SECRET" {
  description = "S3 Secret required config.production.json"
  value       = "${aws_iam_access_key.boto3.secret}"
}

output "master_public_ip" {
  value = ["${aws_instance.master.public_ip}"]
}
