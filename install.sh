# run with sudo privileges
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

################################################################################
### Configuration Parameters =============================================== ###
################################################################################
N_REPLICAS=3
USERNAME=$(who am i | awk '{print $1}')
PROJECT_BUCKET="gs://$USERNAME-backup"
CLIENT_DIR=$(dirname `dirname $PWD`)/backup
mkdir config
echo "N_REPLICAS=3" >> config/install
echo "USERNAME=$USERNAME" >> config/install
echo "PROJECT_BUCKET=$PROJECT_BUCKET" >> config/install
echo "CLIENT_DIR=$CLIENT_DIR" >> config/install

################################################################################
### Package and Library Installs =========================================== ###
################################################################################

### Python ================================================================= ###
if ! [[ $(which python) ]]; then
  echo "Python is not installed; try again after you've installed it!"
  exit
fi

### Pip ==================================================================== ###
PIP_INSTALLED=$(which pip)
if ! [[ $PIP_INSTALLED ]]; then
  echo "Installing pip (the Python package manager)..."
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  if [ $? -eq 1 ]; then
    echo "Could not download pip"; exit
  fi
  
  sudo -H python get-pip.py &> /dev/null
  if [ $? -eq 1 ]; then
    echo "Could not install pip"; exit
  fi
  
  rm get-pip.py
else
  sudo pip install --upgrade pip &> /dev/null
fi

### Paramiko =============================================================== ###
pip install paramiko --user

### GCloud ================================================================= ###
if ! [ -d ".sdk" ]; then
  echo "Installing the Google Cloud SDK..."
  curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-198.0.0-darwin-x86_64.tar.gz -o sdk.tar.gz
  gunzip -c sdk.tar.gz | tar xopf - &> /dev/null
  rm -rf sdk.tar.gz; mv google-cloud-sdk .sdk
  chown -R $USERNAME .sdk
fi

################################################################################
### Google Cloud Setup ===================================================== ###
################################################################################

export PATH=$PATH:$(pwd)/.sdk/bin

### Login ================================================================== ###
echo "Done! Logging in to Google Cloud now..."
echo ""
echo "-------------------------------------------------------------------------"
echo ""
gcloud config configurations activate default &> /dev/null
gcloud auth login &> /dev/null

### Project================================================================= ###
echo "Login complete! Creating backup project now..."
gcloud projects create $USERNAME-automatic-backup --quiet &> /dev/null
gcloud config set project $USERNAME-automatic-backup --quiet &> /dev/null
gcloud services enable compute.googleapis.com --quiet &> /dev/null

### SSH Keys =============================================================== ###
echo "Instance creation complete! Adding SSH keys now..."
if ! [ -f $HOME/.ssh/google_compute_engine.pub ]; then
  ssh-keygen -t rsa -f $HOME/.ssh/google_compute_engine -N ''
fi
chown 600 $HOME/.ssh/google_compute_engine.pub
chown 600 $HOME/.ssh/google_compute_engine

echo $USERNAME:$(cat $HOME/.ssh/google_compute_engine.pub) > $HOME/.ssh/google_compute_engine.txt
gcloud compute project-info add-metadata --metadata-from-file ssh-keys=$HOME/.ssh/google_compute_engine.txt
rm $HOME/.ssh/google_compute_engine.txt

### Instances ============================================================== ###
echo "Project creation complete! Initializing instances now..."
for i in $(seq 1 $N_REPLICAS); do
  gcloud compute instances create backup-instance$i \
    --metadata-from-file startup-script=startup.sh \
    --metadata username=$USERNAME \
    --zone us-east1-b \
    --machine-type f1-micro \
    --image-family=ubuntu-1604-lts \
    --image-project=ubuntu-os-cloud \
    --scopes=storage-full,https://www.googleapis.com/auth/compute \
    --tags=http-server,https-server \
    --quiet &> /dev/null
done

### IP Addresses =========================================================== ###
gcloud --format="value(networkInterfaces[0].accessConfigs[0].natIP)" compute instances list \
  > config/ips

### SSH Keys =============================================================== ###
mkdir ssh
cp $HOME/.ssh/google_compute_engine ssh
cp $HOME/.ssh/google_compute_engine.pub ssh

### Resource Bucket ======================================================== ###
gsutil mb -l us-east1 $PROJECT_BUCKET
gsutil cp -rom ssh $PROJECT_BUCKET
gsutil cp -rom ftp $PROJECT_BUCKET
gsutil cp -rom config $PROJECT_BUCKET

### Update Cron Job ======================================================== ###
(crontab -l ; echo "0 * * * * python $PWD/ftp/client.py"; echo 'MAILTO=""') | sort - | uniq - | crontab -