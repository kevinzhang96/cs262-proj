import json
import os
import time
from json_helper import Crawler, diff
from connection import SFTPConnection, InfoConnection
from consensus import run_consensus

# Assumes config is replicated in the SAME directory (not above ftp)
ips = filter(len, open("../config/ips").read().split("\n"))
config = open("../config/install").read().split("\n")
username = filter(lambda k: "USERNAME" in k, config)[0].split("=")[1]
SERVER_DIR = "/home/" + username + "/backup"
CLIENT_DIR = "../backup"

try:
    os.makedirs(CLIENT_DIR)
except:
    pass

replica = None
for server_ip in ips:
    print "Connecting to server at address", server_ip, "now..."
    c = InfoConnection(server_ip)
    if not c.connect():
        print "Couldn't connect to", server_ip
    else:
        c.send_replica_ip()
        c.run_consensus()
        # time.sleep(300)
        server_json = c.get_json()
        server_json = json.loads(server_json.replace('\'', '\"'))
        replica = server_ip
        c.close()
        break

if replica is None:
    raise Exception("All servers are down. Download failed.")

client_json = Crawler().dump(CLIENT_DIR)
diffs = diff(server_json, client_json)
(server_files, server_dirs) = diffs[0]
server_dirs.sort(key=lambda d: d.count("/"), reverse=False)

for server_dir in server_dirs:
    print server_dir
    os.makedirs(server_dir[len(SERVER_DIR) + 1:])

print "Trying to establish sftp..."
# Establish a SFTP connection
s = SFTPConnection(CLIENT_DIR, "../ssh/google_compute_engine")
if not s.connect(replica, SERVER_DIR + "/", username):
    print "Couldn't open a file transfer connection to", replica
    raise Exception("Can't transfer files from server.")

# Retrieve all files, and create all directories
try:
    for server_file in server_files:
        print "Retrieving server file", server_file
        server_file = server_file[len(SERVER_DIR) + 1:]
        s.get(server_file)
except IOError as e:
    print "Updating the server failed with error", str(e)