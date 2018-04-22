if ! [[ $(which pip) ]]; then
  echo "Already uninstalled."
  exit
fi

for i in $( pip freeze ); do sudo pip uninstall -y $i &> /dev/null; done

sudo python -m pip uninstall -y pip setuptools &> /dev/null

sudo rm -rf .sdk

echo "Done!"