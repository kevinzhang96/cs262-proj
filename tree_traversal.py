import os
import json
import hashlib

BLOCKSIZE = 65536
# use sha-1 hashing
hasher = hashlib.sha1()
# Store the directory's file structure. Key/Value = path/filename
tree = {}

def file_hash(filename):
	with open(filename, 'rb') as afile:
	    buf = afile.read(BLOCKSIZE)
	    while len(buf) > 0:
	        hasher.update(buf)
	        buf = afile.read(BLOCKSIZE)
	return hasher.hexdigest()

for root, dirs, files in os.walk(".", topdown=False):
	for name in files:
		path = os.path.join(root, name)
		tree[path] = file_hash(os.path.join(root, name))
	for name in dirs:
		tree[os.path.join(root, name)] = 'directory'

# dump the directory tree into JSON file
with open('tree.json', 'w') as outfile:
    json.dump(tree, outfile)
