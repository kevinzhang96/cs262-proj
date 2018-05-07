#! /bin/bash
USERNAME=$(curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/username")
INSTANCE_BUCKET="gs://$USERNAME-$HOSTNAME"
PROJECT_BUCKET="gs://$USERNAME-backup"

cd /home/$USERNAME

if ! [ -d backup ]; then
    export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
    echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
fi

sudo apt-get update
sudo apt-get install -y gcsfuse
sudo apt-get install -y python-pip

pip install paramiko

if ! [ -d "backup" ]; then
    gsutil mb -l us-east1 $INSTANCE_BUCKET
    mkdir backup; gcsfuse $INSTANCE_BUCKET backup
fi

gsutil cp -rom $PROJECT_BUCKET .
cd ftp; sudo python server.py

exit