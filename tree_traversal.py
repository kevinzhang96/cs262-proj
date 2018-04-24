import os
import json
import hashlib

# read big files in 64kb chunks so we don't hog memory
BLOCKSIZE = 65536
# use sha-1 hashing
hasher = hashlib.sha1()
# store the directory's file structure. key/value = path/filename
tree = {}

def file_hash(filename):
	with open(filename, 'rb') as file:
	    buf = file.read(BLOCKSIZE)
	    while len(buf):
	        hasher.update(buf)
	        buf = file.read(BLOCKSIZE)
	return hasher.hexdigest()

for root, dirs, files in os.walk(".", topdown=False):
	for name in files:
		path = os.path.join(root, name)
		tree[path] = file_hash(os.path.join(root, name))
	for name in dirs:
		tree[os.path.join(root, name)] = 'directory'

# dump the directory tree into JSON file
with open('tree.json', 'w') as file:
    json.dump(tree, file)
