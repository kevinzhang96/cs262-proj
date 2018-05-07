# run with sudo privileges
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

################################################################################
### Configuration Parameters =============================================== ###
################################################################################
if ! [ -d "config" ]; then
  mkdir config
fi
rm config/install
rm .log

N_REPLICAS=3
RANDOM_NUM=$(($RANDOM % 10000))
USERNAME=$(who am i | awk '{print $1}')
PROJECT_BUCKET="$USERNAME-backup-$RANDOM_NUM"
CLIENT_DIR=$(dirname `dirname $PWD`)/backup
echo "N_REPLICAS=3" 1>> config/install
echo "RANDOM_NUM=$RANDOM_NUM" 1>> config/install
echo "USERNAME=$USERNAME" 1>> config/install
echo "PROJECT_BUCKET=$PROJECT_BUCKET" 1>> config/install
echo "CLIENT_DIR=$CLIENT_DIR" 1>> config/install

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
  
  sudo -H python get-pip.py 1>> .log 2>&1
  if [ $? -eq 1 ]; then
    echo "Could not install pip"; exit
  fi
  
  rm get-pip.py
  echo "Done."
else
  sudo -H pip install -q --upgrade pip 1>> .log 2>&1
fi

### Paramiko =============================================================== ###
pip install -q --user paramiko 1>> .log 2>&1

### GCloud ================================================================= ###
if ! [ -d ".sdk" ]; then
  echo "Installing the Google Cloud SDK... "
  curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-198.0.0-darwin-x86_64.tar.gz -o sdk.tar.gz
  gunzip -c sdk.tar.gz | tar xopf - 1>> .log 2>&1
  rm -rf sdk.tar.gz; mv google-cloud-sdk .sdk
  chown -R $USERNAME .sdk
  chown -R $USERNAME $HOME/.config
  echo "Done."
fi

################################################################################
### Google Cloud Setup ===================================================== ###
################################################################################

export PATH=$PATH:$(pwd)/.sdk/bin

### Login ================================================================== ###
printf "Logging in to Google Cloud... "
gcloud config configurations activate default 1>> .log 2>&1
gcloud auth login 1>> .log 2>&1
echo "done."

### Project ================================================================ ###
printf "Creating backup project... "
gcloud projects create $USERNAME-backup-$RANDOM_NUM 1>> .log 2>&1
gcloud config set project $USERNAME-backup-$RANDOM_NUM 1>> .log 2>&1
echo "done."

### SSH Keys =============================================================== ###
echo "Project creation complete. Please go to your project page and enable billing."
read -rsp $'Press any key to continue...\n' -n1 key

printf "Attempting to enable compute services..."
gcloud services enable compute.googleapis.com 1>> .log 2>&1
if [ $? -eq 1 ]; then
  echo "Could not enable compute services; please check that you have enabled billing on your project correctly then try again!"
  exit
fi
echo "done."

printf "Adding SSH keys to the project... "
if ! [ -f $HOME/.ssh/google_compute_engine.pub ]; then
  ssh-keygen -t rsa -f $HOME/.ssh/google_compute_engine -N '' 1>> .log 2>&1
fi

echo $USERNAME:$(cat $HOME/.ssh/google_compute_engine.pub) > google_compute_engine.txt
gcloud compute project-info add-metadata --metadata-from-file ssh-keys=google_compute_engine.txt 1>> .log 2>&1
echo "done."

### Instances ============================================================== ###
printf "Initializing backup instances... "
for i in $(seq 1 $N_REPLICAS); do
  gcloud compute instances create backup-$RANDOM_NUM-$i \
    --metadata-from-file startup-script=startup.sh,ssh-keys=google_compute_engine.txt \
    --metadata username=$USERNAME,random_num=$RANDOM_NUM \
    --zone us-east1-b \
    --machine-type f1-micro \
    --image-family=ubuntu-1604-lts \
    --image-project=ubuntu-os-cloud \
    --scopes=storage-full,https://www.googleapis.com/auth/compute \
    --tags=http-server,https-server 1>> .log 2>&1
done
gcloud compute firewall-rules create 'allow-9000-in' --allow tcp:9000,udp:9000,icmp --direction=IN
gcloud compute firewall-rules create 'allow-9000-out' --allow tcp:9000,udp:9000,icmp --direction=OUT
rm google_compute_engine.txt
echo "done."

################################################################################
### Config Setup =========================================================== ###
################################################################################

printf "Taking care of a few last things... "

### IP Addresses =========================================================== ###
gcloud --format="value(networkInterfaces[0].accessConfigs[0].natIP)" compute instances list > config/ips

### SSH Keys =============================================================== ###
if ! [ -d "ssh" ]; then
  mkdir ssh
fi
cp $HOME/.ssh/google_compute_engine ssh
cp $HOME/.ssh/google_compute_engine.pub ssh

### Resource Bucket ======================================================== ###
gsutil mb -l us-east1 gs://$PROJECT_BUCKET 1>> .log 2>&1
gsutil cp -r ssh gs://$PROJECT_BUCKET 1>> .log 2>&1
gsutil cp -r ftp gs://$PROJECT_BUCKET 1>> .log 2>&1
gsutil cp -r config gs://$PROJECT_BUCKET 1>> .log 2>&1

### Update Cron Job ======================================================== ###
(crontab -l ; echo "0 * * * * python $PWD/ftp/client.py"; echo 'MAILTO=""') | sort - | uniq - | crontab -

echo "done!"
echo "Good to go!"