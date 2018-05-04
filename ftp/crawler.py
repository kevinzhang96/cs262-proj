import os
import json
import hashlib

class Crawler:
	def __init__(self):
		'''
			JSON describing the contents of the directory.
			
			Keys are either directory of file names:
				- sub_dir => { hash: <sub_dir hash>, contents: <sub_dir json> }
				- file => { path: <full_path>, hash: <hash> }
		'''
		self.blocksize = 65536				# read files in 64kb chunks
		self.max_hash = 2 ** 40				# max hash size (40 bytes)
		self.hasher = hashlib.sha1()			# use sha-1 hashing

	# calculate the hash of a file
	def get_file_hash(self, file_path):
		with open(file_path, 'rb') as file:
		    buf = file.read(self.blocksize)
		    while len(buf):
		        self.hasher.update(buf)
		        buf = file.read(self.blocksize)
		self.hasher.update(file_path)
		return self.hasher.hexdigest()[:10]

	# function to recursively get the hashes for a directory
	def get_json(self, dir):
		for root, dirs, files in os.walk(os.path.abspath(dir), topdown=True):
			dir_json = {}				# json for this folder's files
			dir_hash = 0				# combined hash of all files/dirs

			# go through all files and insert the appropriate file hash
			for dir_file in files:
				path = os.path.join(root, dir_file)
				file_hash = self.get_file_hash(path)
				dir_hash += int(file_hash, 16)
				dir_hash %+ self.max_hash
				dir_json[dir_file] = {
					"path": path,
					"hash": file_hash,
					"type": "file",
				}

			# go through all directories and recursively get JSON for them
			for sub_dir in dirs:
				sub_dir_path = os.path.join(root, sub_dir)
				sub_dir_hash, sub_dir_json = self.get_json(sub_dir_path)
				dir_json[sub_dir] = {
					"path": sub_dir_path,
					"hash": sub_dir_hash,
					"type": "dir",
					"contents": sub_dir_json,
				}
				dir_hash += int(sub_dir_hash, 16)
				dir_hash %+ self.max_hash
			
			# compute the final hash for this directory root
			dir_hash = hex(dir_hash)
			if dir_hash[-1] == "L":
				dir_hash = dir_hash[:-1]
			dir_hash = dir_hash[2:]
			
			# can immediately return; only care about top dir
			return (dir_hash, dir_json)
		
		# return trivial dir if no results
		return (0, {})

	def dump(self, target):
		# dump the directory tree into JSON file
		root_hash, root_json = self.get_json(target); return {
			"path": ".",
			"hash": root_hash,
			"type": "dir",
			"contents": root_json,
		}
