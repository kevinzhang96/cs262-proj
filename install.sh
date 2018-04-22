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

# check to make sure pip is installed
if ! [[ $(which pip) ]]; then
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

echo "Done!"