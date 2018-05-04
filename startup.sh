#! /bin/bash
if ! [ -d backup ]; then
    export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
    echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
fi

sudo apt-get update
sudo apt-get install -y gcsfuse
sudo apt-get install -y python-pip

if ! [ -d backup ]; then
    gsutil mb -l us-east1 gs://$USER-$HOSTNAME
    mkdir backup; gcsfuse $USER-$HOSTNAME backup
fi

gsutil cp -r gs://$USER-backup/* .
cd ftp; sudo python server.py