if ! [[ $(which pip) ]]; then
  echo "Already uninstalled."
  exit
fi

# first delete the project off of Google Cloud
.sdk/bin/gcloud projects delete $USER-automatic-backup --quiet &> /dev/null

# uninstall pip and its packages
for i in $( pip freeze ); do sudo pip uninstall -y $i &> /dev/null; done
sudo python -m pip uninstall -y pip setuptools &> /dev/null

# remove the SDK and configs
sudo rm -rf .sdk
sudo rm -rf ~/.config/gcloud

echo "Done!"