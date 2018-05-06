import time
from crawler import Crawler
from assistant import SFTPAssistant
from util import createSocket

# all of these should be moved elsewhere
NUM_REPLICAS = 1
# should be moved to install.sh later
REPLICA_IPS = {}
REPLICA_IPS[0] = "35.231.73.209"
SSH_PATH = "/Users/tomoya/.ssh/gcloud"
REMOTE_PATH = "/home/tomoya/backup"
LOCAL_PATH = "/Users/tomoya/coursework/CS262/cs262-proj/ftp"
USER_NAME = "tomoya"
TIMEOUT = 60

for replica in range(NUM_REPLICAS):
	sftp = SFTPAssistant(LOCAL_PATH, SSH_PATH)
	start_time = time.time()
	n = 1
	while not sftp.connect(REPLICA_IPS[replica], REMOTE_PATH, USER_NAME):
		if time.time() >= start_time + TIMEOUT:
			raise Exception("Server connection timed out.")
		time.sleep(2**n)
		n += 1

	# crawl through LOCAL_PATH and recursively transfer all files/directories
	sftp.upload_all()
	sftp.close()

class ReplicaConnection():
	def __init__(self, ip_addr):
		self.replica_ip = ip_addr
		self.sock = None

	def connect(self):
		assert self.sock is None
		self.sock = createSocket()
		self.sock.connect((self.replica_ip, 9000))

	def close(self):
		assert self.sock is not None
		self.sock.close()
		self.sock = None

	def get_json(self):
		assert self.sock is not None
		self.sock.send("0")
		json = ''
		while True:
			part = self.sock.recv(1024)
			json += part
			if part < 1024:
				break
		return json

	def run_consensus(self):
		assert self.sock is not None
		self.sock.send("1")

	def send_replica_ip(self):
		assert self.sock is not None
		self.sock.send("2" + str(len(self.replica_ip)) + self.replica_ip)

	def send_peer_ips(self, ips):
		assert self.sock is not 
		self.sock.send()
