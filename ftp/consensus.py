import json
from crawler import Crawler

'''
	Walks through a directory and returns a list of all files and folders
	contained inside it.

	Returns:
	(
		[ <list of files in the directory> ],
		[ <list of folders in the directory> ]
	)
'''
def walk(dir):
	assert dir['type'] == 'dir'
	files, folders = [], []
	for name, obj in dir['contents'].items():
		if obj['type'] == 'file':
			files.append(obj['path'])
		else:
			folders.append(obj['path'])
			subfiles, subfolders = walk(obj)
			files += subfiles
			folders += subfolders
	return files, folders

'''
	Calculates all files and folders unique to a JSON object vs. another JSON
	object.  Both JSON objects should be formatted according to our Crawler.

	Returns:
	(
		[ <list of files unique to dir1> ],
		[ <list of folders unique to dir1> ]
	)
'''
def diff_helper(dir1, dir2):
	if dir1['hash'] == dir2['hash']:
		return []

	files, folders = [], []
	for name, obj in dir1['contents'].items():
		assert obj['type'] == 'file' or obj['type'] == 'dir'
		if obj['type'] == 'file':
			if not (
				name in dir2['contents']
				and dir2['contents'][name]['hash'] == obj['hash']
				and dir2['contents'][name]['type'] == 'file'
			):
				files.append(obj['path'])
		
		if obj['type'] == 'dir':
			if name not in dir2['contents'] or dir2['contents'][name]['type'] == 'file':
				r = walk(obj)
				files += r[0]
				folders.append(obj['path'])
				folders += r[1]
				continue
			if dir2['contents'][name]['hash'] == obj['hash']:
				continue
			r = diff_helper(obj, dir2['contents'][name])
			files += r[0]
			folders += r[1]
	return files, folders

'''
	Calculates the difference between two JSON objects returned by our Crawler
	class, describing two different directories.

	Returns a tuple of the following form:
	(
		(
			[ <list of files unique to dir1> ],
			[ <list of dirs unique to dir1> ]
		),
		(
			[ <list of files unique to dir2> ],
			[ <list of dirs unique to dir2> ]
		)
	)
'''
def diff(dir1, dir2):
	assert dir1['type'] == 'dir' and dir2['type'] == 'dir'
	return (diff_helper(dir1, dir2), diff_helper(dir2, dir1))