import os
import json
import hashlib

'''
	JSON describing the contents of the directory.
	
	Keys are either directory of file names:
		- sub_dir => { hash: <sub_dir hash>, contents: <sub_dir json> }
		- file => { path: <full_path>, hash: <hash> }
'''
tree = {}

BLOCKSIZE = 65536				# read files in 64kb chunks
MAX_HASH = 2 ** 40				# max hash size (40 bytes)
dir_hashes = {}					# dir path => hash pairs
hasher = hashlib.sha1()			# use sha-1 hashing

# calculate the hash of a file
def get_file_hash(file_path):
	with open(file_path, 'rb') as file:
	    buf = file.read(BLOCKSIZE)
	    while len(buf):
	        hasher.update(buf)
	        buf = file.read(BLOCKSIZE)
	hasher.update(file_path)
	return hasher.hexdigest()[:10]

# function to recursively get the hashes for a directory
def get_json(dir):
	for root, dirs, files in os.walk(dir, topdown=True):
		dir_json = {}				# json for this folder's files
		dir_hash = 0				# combined hash of all files/dirs

		# go through all files and insert the appropriate file hash
		for dir_file in files:
			path = os.path.join(root, dir_file)
			file_hash = get_file_hash(path)
			dir_hash += int(file_hash, 16)
			dir_hash %+ MAX_HASH
			dir_json[dir_file] = {
				"path": path,
				"hash": file_hash,
				"type": "file",
			}

		# go through all directories and recursively get JSON for them
		for sub_dir in dirs:
			sub_dir_path = os.path.join(root, sub_dir)
			sub_dir_hash, sub_dir_json = get_json(sub_dir_path)
			dir_json[sub_dir] = {
				"path": sub_dir_path,
				"hash": sub_dir_hash,
				"type": "dir",
				"contents": sub_dir_json,
			}
			dir_hash += int(sub_dir_hash, 16)
			dir_hash %+ MAX_HASH
		
		# compute the final hash for this directory root
		dir_hash = hex(dir_hash)
		if dir_hash[-1] == "L":
			dir_hash = dir_hash[:-1]
		dir_hash = dir_hash[2:]
		
		# can immediately return; only care about top dir
		return (dir_hash, dir_json)

# dump the directory tree into JSON file
with open('tree.json', 'w') as file:
    root_hash, root_json = get_json("."); json.dump({
		"path": ".",
		"hash": root_hash,
		"type": "dir",
		"contents": root_json,
	}, file)
