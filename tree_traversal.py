import os
import json
import hashlib

# read big files in 64kb chunks so we don't hog memory
BLOCKSIZE = 65536
MAX_HASH = 2 ** 40
# use sha-1 hashing
hasher = hashlib.sha1()
# store the directory's file structure. key/value = path/filename
tree = {}

def get_file_hash(filename):
	with open(filename, 'rb') as file:
	    buf = file.read(BLOCKSIZE)
	    while len(buf):
	        hasher.update(buf)
	        buf = file.read(BLOCKSIZE)
	return hasher.hexdigest()[:10]

for root, dirs, files in os.walk(".", topdown=False):
	# take off leading ./
	root = root[2:]
	
	# json for this folder's files
	root_json = {}
	
	# combined hash of all files in this directory
	root_hash = 0
	
	# iterate through all files and store hashes + paths
	for name in files:
		path = os.path.join(root, name)
		file_hash = get_file_hash(path)
		root_hash += int(file_hash, 16)
		root_hash %= MAX_HASH
		root_json[name] = {
			"path": path, 
			"hash": file_hash
		}
	
	# add hashes of all folders here to this directory's hash
	for name in dirs:
		root_hash += int(tree[name]['hash'], 16)
		root_hash %= MAX_HASH
	
	# insert this directory's hash and contents
	root_hash = hex(root_hash)
	if root_hash[-1] == "L":
		root_hash = root_hash[:-1]
	tree[root] = {
		'hash': root_hash[2:],
		'contents': root_json
	}

# dump the directory tree into JSON file
with open('tree.json', 'w') as file:
    json.dump(tree, file)
