#! /bin/bash
USERNAME=$(curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/username")
RANDOM_NUM=$(curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/random_num")
INSTANCE_BUCKET="$USERNAME-$HOSTNAME"
PROJECT_BUCKET="$USERNAME-backup-$RANDOM_NUM"

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
    gsutil mb -l us-east1 gs://$INSTANCE_BUCKET
    sudo -u $USERNAME mkdir backup
    sudo -u $USERNAME gcsfuse $INSTANCE_BUCKET backup
fi

sudo gsutil cp -r gs://$PROJECT_BUCKET/* .
sudo chown -R $USERNAME:$USERNAME **
cd ftp; sudo -u $USERNAME python server.py &> ../.log

exit