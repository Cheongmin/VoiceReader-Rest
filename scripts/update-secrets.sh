#!/usr/bin/env bash

files=('firebase-adminsdk.json' 'voicereader-vm.pem')

echo ${files[@]}
tar -cvzf secrets.tar ${files[@]}