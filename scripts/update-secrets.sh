#!/usr/bin/env bash

files=('firebase-adminsdk.json' 'voicereader-vm.pem' 'config.production.json')

echo ${files[@]}
tar -cvzf secrets.tar ${files[@]}