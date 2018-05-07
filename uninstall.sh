if ! [[ $(which pip) ]]; then
  echo "Already uninstalled."
  exit
fi

# delete the project off of Google Cloud
source config/install
$PROJECT=$USERNAME-backup-$RANDOM_NUM
.sdk/bin/gcloud projects delete $PROJECT --quiet &> /dev/null

# uninstall pip and its packages
for i in $( pip freeze ); do sudo pip uninstall -y $i &> /dev/null; done
sudo python -m pip uninstall -y pip setuptools &> /dev/null

# remove the SDK and configs
sudo rm -rf .sdk
sudo rm -rf ~/.config/gcloud
sudo rm -rf ssh ips.txt

echo "Done!"