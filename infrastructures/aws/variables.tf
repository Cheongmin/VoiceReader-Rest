variable "s3_resource_name" {
  default = "voicereader-resource-prod"
}

variable "default_profile_path" {
  default = "../../static/images/default_user_profile.png"
}

variable "iam_boto_s3" {
  default = "boto_for_s3"
}

variable "key_pair_name" {
  default = "ec2-key"
}

variable "pri_key_path" {
  default = "terraform_ec2_key"
}

// ssh-keygen -t rsa -b 4096 -f terraform_ec2_key
// openssl req -x509 -days 365 -new -key terraform_ec2_key -out terraform_ec2_key.pem
variable "pub_key_path" {
  default = "terraform_ec2_key.pub"
}

variable "bootstrap_path" {
  default = ""
}

variable "ami" {
  description = "Amazon Linux AMI"
  default     = "ami-018a9a930060d38aa"
}

variable "instance_type" {
  description = "Instance type"
  default     = "t2.micro"
}

variable "default_ec2_username" {
  default = "ec2-user"
}

variable "docker_package_version" {
  default = "docker-18.06.1ce"
}
