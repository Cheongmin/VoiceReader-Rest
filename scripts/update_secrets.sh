#!/usr/bin/env bash

files=('firebase-adminsdk.json' 'infrastructures/aws/terraform_ec2_key' 'config.production.json')

echo ${files[@]}
tar -cvzf secrets.tar ${files[@]}