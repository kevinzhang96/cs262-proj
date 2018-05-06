import socket
import sys

def createSocket():
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, e:
        print "Error: could not create socket, {}".format(e)
        sys.exit()
    assert sock is not None
    return sock