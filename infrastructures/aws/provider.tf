terraform {
  required_version = "= 0.11.11"

  # Backend Settings
  backend "s3" {
    # s3 bucket name
    bucket = "voicereader-terraforms"

    # store file name
    key = "terraform.tfstate"

    # s3 bucket region
    region = "ap-northeast-2"

    # s3 encrypt
    encrypt = true
  }
}

provider "aws" {
  region = "ap-northeast-2"
}
