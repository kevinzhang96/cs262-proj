from crawler import Crawler
from assistant import SFTPAssistant

# all of these should be moved elsewhere
NUM_REPLICAS = 1
# should be moved to install.sh later
REPLICA_IPS = {}
REPLICA_IPS[0] = "35.231.73.209"
SSH_PATH = "/Users/tomoya/.ssh/gcloud"
REMOTE_PATH = "/home/tomoya/backup"
LOCAL_PATH = "/Users/tomoya/coursework/CS262/cs262-proj/ftp"
USER_NAME = "tomoya"

for replica in range(NUM_REPLICAS):
	sftp = SFTPAssistant(LOCAL_PATH, SSH_PATH)
	if not sftp.connect(REPLICA_IPS[replica], REMOTE_PATH, USER_NAME):
		print "Couldn't connect"
		# handle connection failure with exponential backoff + timeout + server reboot etc

	# crawl through LOCAL_PATH and recursively transfer all files/directories
	sftp.upload_all()
	sftp.close()
