(crontab -l ; echo "* * * * * cd $PWD && python client.py") | sort - | uniq - | crontab -