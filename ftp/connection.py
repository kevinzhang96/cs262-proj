import os
import paramiko
import time
from util import create_socket

TIMEOUT = 60

class SFTPConnection:
	def __init__(self, local, ssh):
		'''
			Utility class; connects to a remote host given the appropriate local
			and remote folder prefixes. For the Google Cloud instances, the 
			prefix is probably "../backup"; the client prefix shouldn't be known 
			except by the client.
		'''
		self.l_path = local
		self.ssh_file = ssh

	def connect(self, ip, remote, username):
		self.host = ip
		self.r_path = remote
		self.u_name = username
		
		start_time = time.time()
		backoff = 1
		while time.time() < start_time + TIMEOUT:
			try:
				ssh_client = paramiko.SSHClient()
				ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh_client.connect(
					hostname=ip,
					username=username,
					key_filename=self.ssh_file,
					timeout=TIMEOUT
				)
				self.ssh_client = ssh_client

				ftp_client = ssh_client.open_sftp()
				ftp_client.chdir(self.r_path)
				self.ftp_client = ftp_client
				return 1
			except:
				self.ssh_client = None
				self.ftp_client = None
				time.sleep(backoff)
				backoff *= 2
				continue
		return 0

	def close(self):
		if self.ssh_client:
			self.ssh_client.close()
		if self.ftp_client:
			self.ftp_client.close()
		
		self.host = None
		self.r_path = None
		self.u_name = None
		self.ssh_client = None
		self.ftp_client = None

	def get(self, file):
		if not self.ssh_client or not self.ftp_client:
			raise Exception
		self.ftp_client.get(os.path.join(self.r_path, file), file)

	def put(self, file):
		if not self.ssh_client or not self.ftp_client:
			raise Exception
		self.ftp_client.put(os.path.join(self.l_path, file), file)

	def mkdir(self, dir):
		if not self.ssh_client or not self.ftp_client:
			raise Exception
		self.ftp_client.mkdir(dir)

	def rm(self, file):
		if not self.ssh_client or not self.ftp_client:
			raise Exception
		self.ftp_client.remove(file)

	def rmdir(self, dir):
		if not self.ssh_client or not self.ftp_client:
			raise Exception
		self.ftp_client.rmdir(dir)

	def upload_all(self):
		for root, dirs, files in os.walk(self.l_path, topdown=True):
			# go through all files and transfer them to remote
			for dir_file in files:
				path = os.path.join(root, dir_file)
				self.put(path[len(self.l_path):])

			# go through all directories and create them on remote
			for sub_dir in dirs:
				sub_dir_path = os.path.join(root, sub_dir)
				self.mkdir(sub_dir_path[len(self.l_path):])

	def download_all(self):
		raise Exception


class InfoConnection():
	def __init__(self, ip_addr):
		self.replica_ip = ip_addr
		self.sock = None

	def connect(self):
		assert self.sock is None
		start_time = time.time()
		backoff = 1
		while time.time() < start_time + TIMEOUT:
			try:
				self.sock = create_socket()
				self.sock.connect((self.replica_ip, 9000))
				return 1
			except:
				self.sock = None
				time.sleep(backoff)
				backoff *= 2
				continue
		return 0

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
			if len(part) < 1024:
				break
		return json

	def run_consensus(self):
		assert self.sock is not None
		self.sock.send("1")

	def send_replica_ip(self):
		assert self.sock is not None
		self.sock.send("2" + str(len(self.replica_ip)) + self.replica_ip)