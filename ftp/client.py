import json
import random
import time
from json_helper import Crawler, diff
from connection import SFTPConnection, InfoConnection
from consensus import run_consensus

ips = filter(len, open("../config/ips").read().split("\n"))
config = open("../config/install").read().split("\n")
username = filter(lambda k: "USERNAME" in k, config)[0].split("=")[1]
CLIENT_BACKUP_DIR = filter(lambda k: "CLIENT_DIR" in k, config)[0].split("=")[1]
SERVER_BACKUP_DIR = "/home/" + username + "/backup"
client_json = Crawler().dump(CLIENT_BACKUP_DIR)

for server_ip in ips:
    c = InfoConnection(server_ip)
    c.connect()
    server_json = c.get_json()
    server_json = json.loads(server_json.replace('\'', '\"'))

    diffs = diff(server_json, client_json)
    (server_files, server_dirs) = diffs[0]
    (client_files, client_dirs) = diffs[1]

    s = SFTPConnection(CLIENT_BACKUP_DIR, "../ssh/google_compute_engine")
    if s.connect(server_ip, SERVER_BACKUP_DIR + "/", username) == 0:
        print "Connecting to", server_ip, "failed."
        continue
    for server_file in server_files:
        server_file = server_file[len(SERVER_BACKUP_DIR) + 1:]
        s.rm(server_file)
    for server_dir in server_dirs:
        server_dir = server_dir[len(SERVER_BACKUP_DIR) + 1:]
        s.rmdir(server_dir)
    for client_dir in client_dirs:
        client_dir = client_dir[len(CLIENT_BACKUP_DIR) + 1:]
        s.mkdir(client_dir)
    for client_file in client_files:
        print client_file
        client_file = client_file[len(CLIENT_BACKUP_DIR) + 1:]
        print client_file
        s.put(client_file)

leader = random.choice(ips)
run_consensus(leader, ips)