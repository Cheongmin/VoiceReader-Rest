VoiceReader-REST API
====================
[![Build Status](https://travis-ci.org/Cheongmin/VoiceReader-Rest.svg?branch=dev)](https://travis-ci.org/Cheongmin/VoiceReader-Rest)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/55bdba64dd1a475bbfbd743a60056b39)](https://www.codacy.com/app/cheongmin/VoiceReader-Rest?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Cheongmin/VoiceReader-Rest&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/55bdba64dd1a475bbfbd743a60056b39)](https://www.codacy.com/app/cheongmin/VoiceReader-Rest?utm_source=github.com&utm_medium=referral&utm_content=Cheongmin/VoiceReader-Rest&utm_campaign=Badge_Coverage)

This project provides the resource that needs Android App(VoiceReader).

Project Setup
---------------
#### 0. Install Terraform and Ansible
```bash
brew install terraform
terraform --version

brew install ansible
ansible --version
```

#### 1. Create new IAM for terraform

#### 2. Create new S3 to store terraform state file

#### 3. Set environment variables
```bash
export AWS_ACCESS_KEY_ID="<AWS_ACCESS_KEY_ID>"          # access_key
export AWS_SECRET_ACCESS_KEY="<AWS_SECRET_ACCESS_KEY>"  # secret_key
```

#### 4. Terraform Init
```bash
terraform init
```

#### 5. Terraform Plan
```bash
terraform plan
```

#### 6. Create aws resources
```bash
terraform apply
```

#### 7. Update config.json
#### 8. Update TravisCI envvars