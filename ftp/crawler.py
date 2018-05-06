import os
import json
import hashlib

'''
	Utility class used to calculate a JSON description of a desired directory.

	Objects are either files or directories, and have the following properties:
	- Directory: hash, contents, name, path
	- File: hash, name, path

	The value of `contents` in a directory JSON object is a dictionary with
	object names for keys and objects for values. An example JSON object is
	below:

	{
		"type": "dir",
		"name": "foo",
		"hash": "14aw9awrn2",
		"contents": {
			"bar": {
				"type": "file",
				"name": "bar",
				"hash": "13awmo149"
			},
			"empty": {
				"type": "dir",
				"name": "empty",
				"hash": "a14goian",
				"contents": {}
			}
		}
	}

	The above JSON describes the directory below:
	d foo
		f bar
		d empty

	File hashes are completely dependent on the file's contents, while directory
	hashes are dependent both on the contents of the directory and the directory
	location.
'''
class Crawler:
	def __init__(self):
		self.blocksize = 65536				# read files in 64kb chunks
		self.max_hash = 2 ** 40				# max hash size (40 bytes)

	# calculate the hash of a file using SHA-1
	# hash depends completely on file contents
	def get_file_hash(self, file_path):
		hasher = hashlib.sha1()
		with open(file_path, 'rb') as file:
		    buf = file.read(self.blocksize)
		    while len(buf):
		        hasher.update(buf)
		        buf = file.read(self.blocksize)
		return hasher.hexdigest()[:10]

	# computes the JSON described above for a given directory
	def get_json(self, dir):
		if not os.path.isdir(dir):
			raise Exception

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
		
		# if we get here, something went wrong
		raise Exception

	def dump(self, target):
		if not os.path.isdir(target):
			raise Exception

		# dump the directory tree into JSON file
		root_hash, root_json = self.get_json(target)
		return {
			"path": os.path.abspath(target),
			"hash": root_hash,
			"type": "dir",
			"contents": root_json,
		}
