# run with sudo privileges
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

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

# ### Get random seed ======================================================== ###
echo "What was your project identifier?"
while true; do
  read input
  if ! [ "$input" -eq "$input" ] 2> /dev/null; then
    echo "Error: not an integer";
  elif [ "$input" -lt 0 -o "$input" -gt 10000 ]; then
    echo "Error: integer needs to be between 0 and 10000";
  else break;
  fi
done

### Download all files ===================================================== ###
RANDOM_NUM=$input
USERNAME=$(who am i | awk '{print $1}')
echo "Downloading config files..."
mkdir backup_bucket
.sdk/bin/gsutil cp -r gs://$USERNAME-backup-$RANDOM_NUM/* backup_bucket
shopt -s dotglob
sudo chown -R $USERNAME:staff backup_bucket/**
shopt -u dotglob

### Run Python downloader script =========================================== ###
echo "Downloading backup files now..."
mv download.py backup_bucket/ftp/
cd backup_bucket/ftp
sudo -u $USERNAME python download.py
if [ $? -eq 1 ]; then
  echo "Downloading the backup failed; sorry :("
else
  echo "Successfully downloaded the backup!"
fi
mv download.py ../../
cd ../../
sudo rm -rf backup_bucket .log &> /dev/null
sudo rm -rf .sdk