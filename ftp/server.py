import json
import os
import socket
import sys
import threading
import time
from consensus import run_consensus
from json_helper import Crawler
from util import create_socket

PORT_NUMBER = 9000
_crawler = Crawler()
config = open("../config/install").read().split("\n")
config = filter(lambda k: "USERNAME" in k, config)[0]
username = config.split("=")[1]
BACKUP_DIR = '/home/' + username + "/backup"
SERVER_IP = None

class ServerHandler(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.shutdown_flag = threading.Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            time.sleep(0.25)
            action = None
            try:
                action = self.conn.recv(1)
            # the socket's broken; break connection
            except socket.error, e:
                if (
                    e.args[0] != errno.EAGAIN and
                    e.args[0] != errno.EWOULDBLOCK
                ):
                    break

            # no action yet or closed socket
            if action is None:
                continue
            if len(action) == 0:
                break

            # perform appropriate action (return JSON or perform consensus)
            print "Got action", action
            if action == "0":
                self.send_json()
            elif action == "1":
                self.consensus()
            elif action == "2":
                self.receive_ip()
            else:
                print "Unknown action", action
                break
        
    def send_json(self):
        self.conn.send(json.dumps(_crawler.dump(BACKUP_DIR)))

    def consensus(self):
        peer_ips = filter(len, open("../config/ips").read().split("\n"))
        run_consensus(SERVER_IP, peer_ips)

    def receive_ip(self):
        ip_len = int(self.conn.recv(2))
        SERVER_IP = self.conn.recv(ip_len)

# create a socket and start listening for connections
sock = create_socket()
try:
    sock.bind(('', PORT_NUMBER))
    sock.listen(1)
except socket.error, e:
    print "Error: could not set up socket!\n", e
    sys.exit()
try:
    while True:
        conn, addr = sock.accept()
        handler = ServerHandler(conn, addr)
        handler.start()
except KeyboardInterrupt:
    # clean shutdown function; stop all handlers and close the socket
    for handler in threading.enumerate():
        if handler == threading.current_thread():
            continue
        handler.shutdown_flag.set()
        handler.join()
    sock.close()
    sys.exit()