import json
import random
import time
from json_helper import Crawler, diff
from connection import SFTPConnection, InfoConnection
from consensus import run_consensus

ips = filter(len, open("../config/ips").read().split("\n"))
config = open("../config/install").read().split("\n")
username = filter(lambda k: "USERNAME" in k, config)[0].split("=")[1]

SERVER_BACKUP_DIR = "/home/" + username + "/backup"
CLIENT_BACKUP_DIR = filter(lambda k: "CLIENT_DIR" in k, config)[0].split("=")[1]
client_json = Crawler().dump(CLIENT_BACKUP_DIR)

for server_ip in ips:
    print "Updating server at address", server_ip, "now..."

    # attempt to grab metadata info about the server instance
    c = InfoConnection(server_ip)
    if not c.connect():
        print "Couldn't get any info from", server_ip
        continue
    
    # grab metadata info
    server_json = c.get_json()
    server_json = json.loads(server_json.replace('\'', '\"'))

    # compute files and folders that need to be changed
    diffs = diff(server_json, client_json)
    (server_files, server_dirs) = diffs[0]
    (client_files, client_dirs) = diffs[1]
    server_dirs.sort(key=lambda d: d.count("/"), reverse=True)
    client_dirs.sort(key=lambda d: d.count("/"), reverse=False)
    
    # attempt to initialize a SFTP connection
    s = SFTPConnection(CLIENT_BACKUP_DIR, "../ssh/google_compute_engine")
    if not s.connect(server_ip, SERVER_BACKUP_DIR + "/", username):
        print "Couldn't open a file transfer connection to", server_ip
        continue

    # go through and transfer all files and folders
    try:
        for server_file in server_files:
            print "Removing server file", server_file
            server_file = server_file[len(SERVER_BACKUP_DIR) + 1:]
            s.rm(server_file)
        for server_dir in server_dirs:
            print "Removing server folder", server_dir
            server_dir = server_dir[len(SERVER_BACKUP_DIR) + 1:]
            s.rmdir(server_dir)
        for client_dir in client_dirs:
            print "Adding client directory", client_dir
            client_dir = client_dir[len(CLIENT_BACKUP_DIR) + 1:]
            s.mkdir(client_dir)
        for client_file in client_files:
            print "Adding client file", client_file
            client_file = client_file[len(CLIENT_BACKUP_DIR) + 1:]
            s.put(client_file)
    except IOError as e:
        print "Updating the server failed with error", str(e)
        continue

leader = random.choice(ips)
run_consensus(leader, ips)