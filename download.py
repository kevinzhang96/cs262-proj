import json
import os
from json_helper import Crawler, diff
from connection import SFTPConnection, InfoConnection
from consensus import run_consensus

# Assumes config is replicated in the SAME directory (not above ftp)
ips = filter(len, open("config/ips").read().split("\n"))
config = open("config/install").read().split("\n")
username = filter(lambda k: "USERNAME" in k, config)[0].split("=")[1]

SERVER_BACKUP_DIR = "/home/" + username + "/backup"

# Can't use CLIENT_DIR from the original config file since the user can choose a new path to download into
CLIENT_BACKUP_DIR = os.path.dirname(os.path.realpath(__file__)) + "/backup"

client_json = Crawler().dump(CLIENT_BACKUP_DIR)

# Establish connection to retrieve backup state

found_replica = False

for server_ip in ips:
    print "Connecting to server at address", server_ip, "now..."
    c = InfoConnection(server_ip)
    if not c.connect():
        print "Couldn't connect to", server_ip
    else:
        c.send_replica_ip()
        c.run_consensus()
        server_json = c.get_json()
        server_json = json.loads(server_json.replace('\'', '\"'))
        found_replica = True

if not found_replica:
    raise Exception("All servers are down. Download failed.")

diffs = diff(server_json, client_json)
(server_files, server_dirs) = diffs[0]
(client_files, client_dirs) = diffs[1]
server_dirs.sort(key=lambda d: d.count("/"), reverse=True)
client_dirs.sort(key=lambda d: d.count("/"), reverse=False)


# Establish a SFTP connection
s = SFTPConnection(CLIENT_BACKUP_DIR, "../ssh/google_compute_engine")
if not s.connect(server_ip, SERVER_BACKUP_DIR + "/", username):
    print "Couldn't open a file transfer connection to", server_ip
    raise Exception("Can't transfer files from server.")

# Retrieve all files, and create all directories
try:
    for server_file in server_files:
        print "Retrieving server file", server_file
        server_file = server_file[len(SERVER_BACKUP_DIR) + 1:]
        s.get(server_file)
    for server_dir in server_dirs:
        print "Replicating server folder", server_dir
        os.mkdir(CLIENT_BACKUP_DIR + server_dir[len(SERVER_BACKUP_DIR)])

except IOError as e:
    print "Updating the server failed with error", str(e)