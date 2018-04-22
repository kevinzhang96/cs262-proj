# run with sudo privileges
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# check to make sure python is installed
if ! [[ $(which python) ]]; then
  echo "Python is not installed; try again after you've installed it!"
  exit
fi

PIP_INSTALLED=$(which pip)

# check to make sure pip is installed
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

# install google cloud sdk
if ! [ -d ".sdk" ]; then
  echo "Installing the Google Cloud SDK..."
  curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-198.0.0-darwin-x86_64.tar.gz -o sdk.tar.gz
  gunzip -c sdk.tar.gz | tar xopf - &> /dev/null
  sudo rm -rf sdk.tar.gz; sudo mv google-cloud-sdk .sdk
fi

# login to google cloud now
echo "Done! Logging in to Google Cloud now..."
echo ""
echo "-------------------------------------------------------------------------"
echo ""

.sdk/bin/gcloud config configurations activate default &> /dev/null
.sdk/bin/gcloud auth login &> /dev/null

if [ $? -eq 1 ]; then
  echo "Google Cloud login failed.  Reverting installation..."
  if ! [[ $PIP_INSTALLED ]]; then
    for i in $( pip freeze ); do sudo pip uninstall -y $i &> /dev/null; done
    sudo python -m pip uninstall -y pip setuptools &> /dev/null
  fi

  sudo rm -rf .sdk
  sudo rm -rf ~/.config/gcloud
  exit
fi

# create project for backup instances
echo "Login complete! Creating backup project now..."
.sdk/bin/gcloud projects create $USER-automatic-backup --quiet &> /dev/null
.sdk/bin/gcloud config set project $USER-automatic-backup --quiet &> /dev/null
.sdk/bin/gcloud services enable compute.googleapis.com --quiet &> /dev/null

# begin creating instances on google cloud
echo "Project creation complete! Initializing instances now..."
.sdk/bin/gcloud compute instances create backup-instance1 --zone us-east1-b --machine-type f1-micro --quiet &> /dev/null